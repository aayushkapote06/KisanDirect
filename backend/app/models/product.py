"""
models/product.py - Product Database Model

This file defines the "products" table.

Each product is listed by a farmer and has:
- A name (e.g., "Basmati Rice")
- A category (e.g., "Grains")
- A price (in INR per unit)
- A unit (e.g., "kg", "quintal")
- A quantity available
- Whether it's currently available for purchase
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database import Base


class Product(Base):
    """
    The Product table stores all agricultural products listed by farmers.
    
    Each product belongs to one farmer (the farmer_id column links to the users table).
    This is called a "foreign key" relationship - it connects two tables together.
    """
    
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    
    # Which farmer listed this product?
    # ForeignKey("users.id") means this column references the "id" column in the "users" table
    farmer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Product details
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String, nullable=False, index=True)
    
    # Pricing - all prices are in Indian Rupees (INR)
    price = Column(Float, nullable=False)
    
    # Unit of measurement: "kg", "quintal", "tonne", "piece", "dozen", "litre"
    unit = Column(String, nullable=False, default="kg")
    
    # How much is available for sale right now
    quantity_available = Column(Float, nullable=False, default=0)
    
    # Minimum order quantity (useful for bulk items)
    min_order_quantity = Column(Float, nullable=False, default=1)
    
    # Is this product currently available for purchase?
    is_available = Column(Boolean, default=True)
    
    # Optional: image filename (we'll add image upload later)
    image = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship: connect to the User who owns this product
    # This lets us do product.farmer to get the farmer's info
    farmer = relationship("User", backref="products")
