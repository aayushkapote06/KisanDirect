"""
routers/orders.py - Order API Endpoints

This file defines the API endpoints for:
- POST   /api/orders              → Place a new order (consumer/bulk_buyer)
- GET    /api/orders/my           → Get current user's orders (buyer view)
- GET    /api/orders/farmer/me    → Get orders for current farmer's products
- GET    /api/orders/{id}         → Get a single order's details
- PUT    /api/orders/{id}/status  → Update order status (farmer/admin)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.product import Product
from app.models.order import Order, OrderItem
from app.schemas.order import OrderCreate, OrderResponse, OrderItemResponse, OrderStatusUpdate
from app.services.auth import get_current_user, require_role

router = APIRouter(prefix="/api/orders", tags=["Orders"])


def build_order_response(order: Order, db: Session) -> OrderResponse:
    """Helper to build an order response with item details."""
    buyer = db.query(User).filter(User.id == order.buyer_id).first()
    
    items = []
    for item in order.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        farmer = db.query(User).filter(User.id == item.farmer_id).first()
        item_resp = OrderItemResponse(
            id=item.id,
            product_id=item.product_id,
            farmer_id=item.farmer_id,
            quantity=item.quantity,
            unit_price=item.unit_price,
            total_price=item.total_price,
            status=item.status,
            product_name=product.name if product else "Deleted Product",
            farmer_name=farmer.full_name if farmer else "Unknown",
        )
        items.append(item_resp)
    
    return OrderResponse(
        id=order.id,
        buyer_id=order.buyer_id,
        status=order.status,
        total_amount=order.total_amount,
        delivery_address=order.delivery_address,
        delivery_city=order.delivery_city,
        delivery_state=order.delivery_state,
        delivery_pincode=order.delivery_pincode,
        payment_status=order.payment_status,
        notes=order.notes,
        created_at=order.created_at,
        items=items,
        buyer_name=buyer.full_name if buyer else "Unknown",
    )


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(require_role(["consumer", "bulk_buyer"])),
    db: Session = Depends(get_db),
):
    """
    Place a new order.
    
    SECURITY:
    - Only consumers and bulk buyers can place orders
    - Prices are ALWAYS taken from the database, never from the frontend
    - Inventory is checked and updated atomically
    - If any product is unavailable or has insufficient quantity, the entire order fails
    """
    
    # Validate all items and calculate totals using SERVER-SIDE prices
    order_items = []
    total_amount = 0
    
    for item in order_data.items:
        # Get the product from the database
        product = db.query(Product).filter(Product.id == item.product_id).first()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {item.product_id} not found."
            )
        
        if not product.is_available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product '{product.name}' is currently unavailable."
            )
        
        if item.quantity < product.min_order_quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Minimum order for '{product.name}' is {product.min_order_quantity} {product.unit}."
            )
        
        if item.quantity > product.quantity_available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Only {product.quantity_available} {product.unit} of '{product.name}' available. You requested {item.quantity}."
            )
        
        # Calculate price using the SERVER'S price, not the client's
        item_total = round(product.price * item.quantity, 2)
        total_amount += item_total
        
        order_items.append({
            "product": product,
            "quantity": item.quantity,
            "unit_price": product.price,
            "total_price": item_total,
            "farmer_id": product.farmer_id,
        })
    
    # Create the order
    new_order = Order(
        buyer_id=current_user.id,
        status="placed",
        total_amount=round(total_amount, 2),
        delivery_address=order_data.delivery_address or current_user.address,
        delivery_city=order_data.delivery_city or current_user.city,
        delivery_state=order_data.delivery_state or current_user.state,
        delivery_pincode=order_data.delivery_pincode or current_user.pincode,
        delivery_latitude=order_data.delivery_latitude or current_user.latitude,
        delivery_longitude=order_data.delivery_longitude or current_user.longitude,
        payment_status="pending",
        notes=order_data.notes,
    )
    
    db.add(new_order)
    db.flush()  # Get the order ID without committing yet
    
    # Create order items and update inventory
    for item_data in order_items:
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=item_data["product"].id,
            farmer_id=item_data["farmer_id"],
            quantity=item_data["quantity"],
            unit_price=item_data["unit_price"],
            total_price=item_data["total_price"],
            status="placed",
        )
        db.add(order_item)
        
        # Reduce available inventory
        item_data["product"].quantity_available -= item_data["quantity"]
        # If no stock left, mark as unavailable
        if item_data["product"].quantity_available <= 0:
            item_data["product"].is_available = False
    
    # Commit everything at once (atomic operation)
    db.commit()
    db.refresh(new_order)
    
    return build_order_response(new_order, db)


@router.get("/my", response_model=List[OrderResponse])
def get_my_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all orders placed by the current user (buyer view)."""
    orders = db.query(Order).filter(
        Order.buyer_id == current_user.id
    ).order_by(Order.created_at.desc()).all()
    
    return [build_order_response(order, db) for order in orders]


@router.get("/farmer/me", response_model=List[OrderResponse])
def get_farmer_orders(
    current_user: User = Depends(require_role(["farmer"])),
    db: Session = Depends(get_db),
):
    """
    Get all orders that contain products from the current farmer.
    
    A farmer sees orders that include at least one of their products.
    """
    # Find order IDs that have items from this farmer
    farmer_order_ids = db.query(OrderItem.order_id).filter(
        OrderItem.farmer_id == current_user.id
    ).distinct().all()
    
    order_ids = [oid[0] for oid in farmer_order_ids]
    
    if not order_ids:
        return []
    
    orders = db.query(Order).filter(
        Order.id.in_(order_ids)
    ).order_by(Order.created_at.desc()).all()
    
    return [build_order_response(order, db) for order in orders]


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get details of a specific order.
    
    SECURITY: Users can only view orders they're authorized to see:
    - Buyers can view their own orders
    - Farmers can view orders containing their products
    - Admins can view any order
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found."
        )
    
    # Check authorization
    is_buyer = order.buyer_id == current_user.id
    is_farmer = db.query(OrderItem).filter(
        OrderItem.order_id == order_id,
        OrderItem.farmer_id == current_user.id
    ).first() is not None
    is_admin = current_user.role == "admin"
    
    if not (is_buyer or is_farmer or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view this order."
        )
    
    return build_order_response(order, db)


@router.put("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update an order's status.
    
    Rules:
    - Farmers can: confirm, prepare, dispatch their order items
    - Buyers can: cancel (only if status is "placed" or "confirmed")
    - Admins can: update any status
    
    Status flow: placed → confirmed → preparing → dispatched → delivered
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found."
        )
    
    new_status = status_update.status
    
    # Define valid transitions
    valid_transitions = {
        "placed": ["confirmed", "cancelled"],
        "confirmed": ["preparing", "cancelled"],
        "preparing": ["dispatched"],
        "dispatched": ["delivered"],
        "delivered": [],
        "cancelled": [],
    }
    
    if new_status not in valid_transitions.get(order.status, []):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot change status from '{order.status}' to '{new_status}'. "
                   f"Valid transitions: {valid_transitions.get(order.status, [])}"
        )
    
    # Authorization checks
    if current_user.role == "admin":
        pass  # Admins can do anything
    elif current_user.role == "farmer":
        # Farmers can confirm, prepare, dispatch
        is_farmer = db.query(OrderItem).filter(
            OrderItem.order_id == order_id,
            OrderItem.farmer_id == current_user.id
        ).first() is not None
        if not is_farmer:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only manage orders for your own products."
            )
        if new_status == "cancelled":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Farmers cannot cancel orders. Ask the buyer or admin."
            )
    elif order.buyer_id == current_user.id:
        # Buyers can only cancel
        if new_status != "cancelled":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Buyers can only cancel orders."
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update this order."
        )
    
    # If cancelling, restore inventory
    if new_status == "cancelled":
        for item in order.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                product.quantity_available += item.quantity
                product.is_available = True
            item.status = "cancelled"
    else:
        # Update all items' status too
        for item in order.items:
            item.status = new_status
    
    order.status = new_status
    db.commit()
    db.refresh(order)
    
    return build_order_response(order, db)
