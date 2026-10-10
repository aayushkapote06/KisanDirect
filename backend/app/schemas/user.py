"""
schemas/user.py - User Schemas (Data Validation)

Schemas define what data looks like when it enters and leaves our API.

Think of schemas like forms:
- UserCreate: The "registration form" - what info you need to sign up
- UserLogin: The "login form" - email and password
- UserResponse: What we send back about a user (NEVER includes the password!)

Pydantic (the library we use) automatically checks:
- Are required fields present?
- Is the email a valid email format?
- Is the data the right type (string, number, etc.)?
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    """Data required to register a new user."""
    email: EmailStr  # Must be a valid email format
    password: str    # Will be hashed before storing - NEVER stored as plain text
    full_name: str
    phone: Optional[str] = None
    role: str = "consumer"  # Default role is "consumer"
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None


class UserLogin(BaseModel):
    """Data required to log in."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Data we send back about a user. Notice: NO password field!"""
    id: int
    email: str
    full_name: str
    phone: Optional[str] = None
    role: str
    is_active: bool
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # Allows converting from database model to this schema


class UserUpdate(BaseModel):
    """Data that can be updated in a user's profile."""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None


class Token(BaseModel):
    """The login response - contains the access token."""
    access_token: str
    token_type: str
    role: str
    user_id: int
    full_name: str
