"""
models/user.py - User Database Model

This file defines the "users" table in our database.

A "model" is a Python class that represents a database table.
Each attribute of the class becomes a column in the table.

For example:
    email = Column(String, unique=True)
    
This creates an "email" column that stores text, and "unique=True"
means no two users can have the same email address.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    """
    The User table stores all registered users: farmers, consumers,
    bulk buyers, logistics providers, and administrators.
    
    We use a single table for all roles (instead of separate tables)
    because the core login information is the same for everyone.
    The "role" column tells us what type of user they are.
    """
    
    # The name of the table in the database
    __tablename__ = "users"

    # Primary key - a unique number assigned to each user automatically
    id = Column(Integer, primary_key=True, index=True)
    
    # Login credentials
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)  # NEVER store plain passwords!
    
    # User's name
    full_name = Column(String, nullable=False)
    
    # Phone number (important for farmers and logistics)
    phone = Column(String, nullable=True)
    
    # Role: "farmer", "consumer", "bulk_buyer", "logistics", "admin"
    role = Column(String, nullable=False, default="consumer")
    
    # Is this account active? Admins can deactivate problematic accounts
    is_active = Column(Boolean, default=True)
    
    # Address information
    address = Column(Text, nullable=True)
    city = Column(String, nullable=True)
    state = Column(String, nullable=True)
    pincode = Column(String, nullable=True)
    
    # Coordinates for mapping and delivery routing
    latitude = Column(String, nullable=True)
    longitude = Column(String, nullable=True)
    
    # Timestamps - automatically set when user registers
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
