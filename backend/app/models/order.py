"""
models/order.py - Order Database Models

This file defines two tables:
1. "orders" - Each order placed by a buyer
2. "order_items" - Each individual product within an order

Why two tables? Because one order can contain multiple products.
For example, a buyer might order 10kg of rice AND 5kg of tomatoes in one order.
The "orders" table stores the overall order info, and "order_items" stores each product line.

Order Status Lifecycle:
    placed → confirmed → preparing → dispatched → delivered
    (can be "cancelled" from "placed" or "confirmed" states)
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class Order(Base):
    """
    The Order table stores each order placed by a consumer or bulk buyer.
    """
    
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    
    # Who placed this order?
    buyer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Order status: "placed", "confirmed", "preparing", "dispatched", "delivered", "cancelled"
    status = Column(String, nullable=False, default="placed")
    
    # Total price of the entire order (calculated by the server, NOT from frontend)
    total_amount = Column(Float, nullable=False, default=0)
    
    # Delivery address
    delivery_address = Column(Text, nullable=True)
    delivery_city = Column(String, nullable=True)
    delivery_state = Column(String, nullable=True)
    delivery_pincode = Column(String, nullable=True)
    delivery_latitude = Column(String, nullable=True)
    delivery_longitude = Column(String, nullable=True)
    
    # Payment status (simulated for MVP - no real money involved)
    # "pending", "paid", "refunded"
    payment_status = Column(String, default="pending")
    
    # Optional notes from the buyer
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    buyer = relationship("User", backref="orders")
    items = relationship("OrderItem", back_populates="order")


class OrderItem(Base):
    """
    Each line item within an order.
    
    For example, if you order 10kg rice and 5kg tomatoes,
    that's ONE order with TWO order items.
    """
    
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    
    # Which order does this item belong to?
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    
    # Which product was ordered?
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    # Which farmer sells this product? (stored for easy lookup)
    farmer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Quantity ordered
    quantity = Column(Float, nullable=False)
    
    # Price per unit AT THE TIME OF ORDER
    # (We save this because the farmer might change the price later,
    #  but the buyer should pay what was listed when they ordered)
    unit_price = Column(Float, nullable=False)
    
    # Total for this line item (quantity × unit_price)
    total_price = Column(Float, nullable=False)
    
    # Item-level status (useful when items come from different farmers)
    status = Column(String, default="placed")
    
    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product")
    farmer = relationship("User", foreign_keys=[farmer_id])
