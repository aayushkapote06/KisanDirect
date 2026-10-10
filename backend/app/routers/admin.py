"""
routers/admin.py - Administrator API Endpoints

This file defines admin-only endpoints for:
- GET    /api/admin/users         → List all users
- PUT    /api/admin/users/{id}/toggle → Activate/deactivate a user
- GET    /api/admin/orders        → List all orders
- GET    /api/admin/stats         → Platform statistics

ALL endpoints here require the "admin" role.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func as sql_func
from typing import List

from app.database import get_db
from app.models.user import User
from app.models.product import Product
from app.models.order import Order, OrderItem
from app.schemas.user import UserResponse
from app.schemas.order import OrderResponse
from app.services.auth import require_role
from app.routers.orders import build_order_response

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/users", response_model=List[UserResponse])
def list_all_users(
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db),
):
    """List all registered users. Admin only."""
    users = db.query(User).order_by(User.created_at.desc()).all()
    return users


@router.put("/users/{user_id}/toggle")
def toggle_user_active(
    user_id: int,
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db),
):
    """
    Activate or deactivate a user account. Admin only.
    
    A deactivated user cannot log in or use the platform.
    Admins cannot deactivate themselves (to prevent lockout).
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )
    
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot deactivate your own account."
        )
    
    user.is_active = not user.is_active
    db.commit()
    
    status_text = "activated" if user.is_active else "deactivated"
    return {"message": f"User {user.full_name} has been {status_text}.", "is_active": user.is_active}


@router.get("/orders", response_model=List[OrderResponse])
def list_all_orders(
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db),
):
    """List all orders on the platform. Admin only."""
    orders = db.query(Order).order_by(Order.created_at.desc()).all()
    return [build_order_response(order, db) for order in orders]


@router.get("/stats")
def get_platform_stats(
    current_user: User = Depends(require_role(["admin"])),
    db: Session = Depends(get_db),
):
    """
    Get platform statistics. Admin only.
    
    Returns counts of users, products, orders, and revenue.
    These are real numbers from the database, not invented figures.
    """
    total_users = db.query(User).count()
    total_farmers = db.query(User).filter(User.role == "farmer").count()
    total_consumers = db.query(User).filter(User.role == "consumer").count()
    total_bulk_buyers = db.query(User).filter(User.role == "bulk_buyer").count()
    total_logistics = db.query(User).filter(User.role == "logistics").count()
    total_products = db.query(Product).count()
    available_products = db.query(Product).filter(Product.is_available == True).count()
    total_orders = db.query(Order).count()
    
    # Calculate revenue from delivered orders only
    delivered_revenue = db.query(sql_func.sum(Order.total_amount)).filter(
        Order.status == "delivered"
    ).scalar() or 0
    
    pending_orders = db.query(Order).filter(
        Order.status.in_(["placed", "confirmed", "preparing"])
    ).count()
    
    return {
        "users": {
            "total": total_users,
            "farmers": total_farmers,
            "consumers": total_consumers,
            "bulk_buyers": total_bulk_buyers,
            "logistics_providers": total_logistics,
        },
        "products": {
            "total": total_products,
            "available": available_products,
        },
        "orders": {
            "total": total_orders,
            "pending": pending_orders,
        },
        "revenue": {
            "total_delivered": round(delivered_revenue, 2),
            "note": "Revenue calculated from delivered orders only.",
        },
    }
