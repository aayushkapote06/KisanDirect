"""
schemas/order.py - Order Schemas (Data Validation)

These schemas validate order data:
- OrderItemCreate: One product in the cart (product_id + quantity)
- OrderCreate: The full order (list of items + delivery info)
- OrderResponse: What we send back about an order
"""

from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime


class OrderItemCreate(BaseModel):
    """One item in the order (e.g., 10 kg of rice)."""
    product_id: int
    quantity: float

    @field_validator("quantity")
    @classmethod
    def quantity_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Quantity must be greater than zero")
        return v


class OrderCreate(BaseModel):
    """Data required to place a new order."""
    items: List[OrderItemCreate]  # List of products and quantities
    delivery_address: Optional[str] = None
    delivery_city: Optional[str] = None
    delivery_state: Optional[str] = None
    delivery_pincode: Optional[str] = None
    delivery_latitude: Optional[str] = None
    delivery_longitude: Optional[str] = None
    notes: Optional[str] = None

    @field_validator("items")
    @classmethod
    def must_have_items(cls, v):
        if len(v) == 0:
            raise ValueError("Order must contain at least one item")
        return v


class OrderItemResponse(BaseModel):
    """Data we send back about one item in an order."""
    id: int
    product_id: int
    farmer_id: int
    quantity: float
    unit_price: float
    total_price: float
    status: str
    product_name: Optional[str] = None
    farmer_name: Optional[str] = None

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    """Data we send back about an order."""
    id: int
    buyer_id: int
    status: str
    total_amount: float
    delivery_address: Optional[str] = None
    delivery_city: Optional[str] = None
    delivery_state: Optional[str] = None
    delivery_pincode: Optional[str] = None
    payment_status: str
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    items: List[OrderItemResponse] = []
    buyer_name: Optional[str] = None

    class Config:
        from_attributes = True


class OrderStatusUpdate(BaseModel):
    """Used to update an order's status."""
    status: str

    @field_validator("status")
    @classmethod
    def status_must_be_valid(cls, v):
        valid = ["placed", "confirmed", "preparing", "dispatched", "delivered", "cancelled"]
        if v not in valid:
            raise ValueError(f"Status must be one of: {', '.join(valid)}")
        return v
