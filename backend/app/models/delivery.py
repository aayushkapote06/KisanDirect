"""
models/delivery.py - Delivery Database Model

This file defines the "deliveries" table.

A delivery links an order to a logistics provider.
It tracks pickup location (farmer), delivery location (buyer),
and the current status of the delivery.

Delivery Status Lifecycle:
    assigned → accepted → picked_up → in_transit → delivered
    (can be "rejected" by logistics provider from "assigned" state)
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class Delivery(Base):
    """
    The Delivery table tracks the logistics of getting products
    from the farmer to the buyer.
    """
    
    __tablename__ = "deliveries"

    id = Column(Integer, primary_key=True, index=True)
    
    # Which order is being delivered?
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    
    # Which logistics provider is handling this delivery?
    logistics_provider_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Delivery status
    status = Column(String, nullable=False, default="assigned")
    
    # Pickup location (farmer's location)
    pickup_address = Column(Text, nullable=True)
    pickup_latitude = Column(String, nullable=True)
    pickup_longitude = Column(String, nullable=True)
    
    # Delivery location (buyer's location)
    delivery_address = Column(Text, nullable=True)
    delivery_latitude = Column(String, nullable=True)
    delivery_longitude = Column(String, nullable=True)
    
    # Estimated distance in kilometers
    estimated_distance_km = Column(Float, nullable=True)
    
    # Estimated delivery time in minutes
    estimated_time_minutes = Column(Float, nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    picked_up_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    order = relationship("Order", backref="delivery")
    logistics_provider = relationship("User", backref="deliveries")
