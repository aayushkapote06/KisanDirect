"""
routers/logistics.py - Logistics Management & Route Optimization Endpoints

This router handles:
- Viewing deliveries
- Assigning orders for logistics delivery
- Updating delivery status lifecycle
- AI/Algorithmic Route Optimization (TSP 2-Opt with distance/time savings)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from app.database import get_db
from app.models.user import User
from app.models.order import Order
from app.models.delivery import Delivery
from app.services.auth import get_current_user, require_role
from app.services.route_optimizer import optimize_delivery_route, haversine_distance

router = APIRouter(prefix="/api/logistics", tags=["Logistics"])


# Schemas for logistics
class DeliveryStatusUpdate(BaseModel):
    status: str  # assigned, accepted, rejected, picked_up, in_transit, delivered
    notes: Optional[str] = None


class AssignDeliveryRequest(BaseModel):
    order_id: int
    logistics_provider_id: Optional[int] = None
    pickup_address: Optional[str] = None
    pickup_latitude: Optional[str] = None
    pickup_longitude: Optional[str] = None
    delivery_address: Optional[str] = None
    delivery_latitude: Optional[str] = None
    delivery_longitude: Optional[str] = None


class RouteStopInput(BaseModel):
    id: Optional[int] = None
    name: str
    address: str
    lat: float
    lng: float
    order_id: Optional[int] = None


class RouteOptimizeRequest(BaseModel):
    depot: RouteStopInput
    stops: List[RouteStopInput]
    avg_speed_kmh: Optional[float] = 35.0


@router.get("/deliveries")
def list_deliveries(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List deliveries.
    - Logistics providers see deliveries assigned to them or unassigned ones.
    - Admins see all deliveries.
    - Farmers and buyers can see deliveries for their orders.
    """
    query = db.query(Delivery)

    if current_user.role == "logistics":
        query = query.filter(
            (Delivery.logistics_provider_id == current_user.id) |
            (Delivery.logistics_provider_id == None)
        )
    elif current_user.role == "admin":
        pass  # sees all
    elif current_user.role == "consumer" or current_user.role == "bulk_buyer":
        # see deliveries where user is the buyer of the order
        user_order_ids = [o.id for o in db.query(Order).filter(Order.buyer_id == current_user.id).all()]
        query = query.filter(Delivery.order_id.in_(user_order_ids))
    else:
        # farmers see deliveries for orders containing their items
        query = query.all()

    deliveries = query.order_by(Delivery.created_at.desc()).all()
    results = []
    for d in deliveries:
        order = db.query(Order).filter(Order.id == d.order_id).first()
        provider = db.query(User).filter(User.id == d.logistics_provider_id).first() if d.logistics_provider_id else None
        results.append({
            "id": d.id,
            "order_id": d.order_id,
            "logistics_provider_id": d.logistics_provider_id,
            "provider_name": provider.full_name if provider else "Unassigned",
            "status": d.status,
            "pickup_address": d.pickup_address,
            "pickup_latitude": d.pickup_latitude,
            "pickup_longitude": d.pickup_longitude,
            "delivery_address": d.delivery_address,
            "delivery_latitude": d.delivery_latitude,
            "delivery_longitude": d.delivery_longitude,
            "estimated_distance_km": d.estimated_distance_km,
            "estimated_time_minutes": d.estimated_time_minutes,
            "notes": d.notes,
            "created_at": d.created_at,
            "order_total": order.total_amount if order else 0,
        })
    return results


@router.post("/deliveries/assign")
def assign_delivery(
    req: AssignDeliveryRequest,
    current_user: User = Depends(require_role(["admin", "farmer", "logistics"])),
    db: Session = Depends(get_db),
):
    """
    Create or assign a delivery for an order.
    """
    order = db.query(Order).filter(Order.id == req.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Check existing delivery
    delivery = db.query(Delivery).filter(Delivery.order_id == req.order_id).first()
    if not delivery:
        delivery = Delivery(
            order_id=req.order_id,
            logistics_provider_id=req.logistics_provider_id or (current_user.id if current_user.role == "logistics" else None),
            status="assigned",
            pickup_address=req.pickup_address or "Farmer Regional Collection Hub",
            pickup_latitude=req.pickup_latitude or "28.6139",
            pickup_longitude=req.pickup_longitude or "77.2090",
            delivery_address=req.delivery_address or order.delivery_address,
            delivery_latitude=req.delivery_latitude or order.delivery_latitude or "28.5355",
            delivery_longitude=req.delivery_longitude or order.delivery_longitude or "77.3910",
        )
        # Calculate estimated distance
        try:
            p_lat = float(delivery.pickup_latitude)
            p_lon = float(delivery.pickup_longitude)
            d_lat = float(delivery.delivery_latitude)
            d_lon = float(delivery.delivery_longitude)
            dist = round(haversine_distance(p_lat, p_lon, d_lat, d_lon), 2)
            delivery.estimated_distance_km = dist
            delivery.estimated_time_minutes = round((dist / 35.0) * 60, 1)
        except Exception:
            delivery.estimated_distance_km = 15.0
            delivery.estimated_time_minutes = 25.0

        db.add(delivery)
    else:
        if req.logistics_provider_id:
            delivery.logistics_provider_id = req.logistics_provider_id
            delivery.status = "assigned"

    db.commit()
    db.refresh(delivery)
    return {"message": "Delivery successfully assigned", "delivery_id": delivery.id, "status": delivery.status}


@router.put("/deliveries/{delivery_id}/status")
def update_delivery_status(
    delivery_id: int,
    update: DeliveryStatusUpdate,
    current_user: User = Depends(require_role(["logistics", "admin"])),
    db: Session = Depends(get_db),
):
    """
    Update delivery status lifecycle:
    assigned → accepted → picked_up → in_transit → delivered (or rejected)
    """
    delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery record not found")

    if current_user.role == "logistics" and delivery.logistics_provider_id and delivery.logistics_provider_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this delivery")

    valid_statuses = ["assigned", "accepted", "rejected", "picked_up", "in_transit", "delivered"]
    if update.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")

    delivery.status = update.status
    if update.notes:
        delivery.notes = update.notes

    # Sync with main order status if delivered
    if update.status == "delivered":
        order = db.query(Order).filter(Order.id == delivery.order_id).first()
        if order:
            order.status = "delivered"
    elif update.status in ["picked_up", "in_transit"]:
        order = db.query(Order).filter(Order.id == delivery.order_id).first()
        if order:
            order.status = "dispatched"

    db.commit()
    db.refresh(delivery)
    return {"message": f"Delivery updated to {delivery.status}", "status": delivery.status}


@router.post("/route-optimize")
def route_optimize(req: RouteOptimizeRequest):
    """
    AI / Heuristic Route Optimization.
    Calculates shortest delivery loop/path, reducing fuel consumption and turnaround time.
    """
    depot_dict = req.depot.model_dump()
    stops_dict = [s.model_dump() for s in req.stops]

    result = optimize_delivery_route(
        depot=depot_dict,
        deliveries=stops_dict,
        avg_speed_kmh=req.avg_speed_kmh or 35.0
    )
    return result
