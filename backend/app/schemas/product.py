"""
schemas/product.py - Product Schemas (Data Validation)

These schemas validate product data:
- ProductCreate: What a farmer sends when adding a new product
- ProductUpdate: What a farmer sends when editing a product
- ProductResponse: What we send back to anyone viewing products
"""

from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime


# Valid units for agricultural products
VALID_UNITS = ["kg", "quintal", "tonne", "piece", "dozen", "litre", "gram"]

# Valid product categories
VALID_CATEGORIES = [
    "Grains", "Vegetables", "Fruits", "Pulses", "Spices",
    "Dairy", "Oilseeds", "Flowers", "Herbs", "Nuts", "Other"
]


class ProductCreate(BaseModel):
    """Data required to add a new product listing."""
    name: str
    description: Optional[str] = None
    category: str
    price: float       # Price in INR per unit
    unit: str = "kg"   # Unit of measurement
    quantity_available: float
    min_order_quantity: float = 1
    
    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, v):
        """Price must be greater than zero."""
        if v <= 0:
            raise ValueError("Price must be greater than zero")
        return v
    
    @field_validator("quantity_available")
    @classmethod
    def quantity_must_not_be_negative(cls, v):
        """Available quantity cannot be negative."""
        if v < 0:
            raise ValueError("Quantity cannot be negative")
        return v

    @field_validator("unit")
    @classmethod
    def unit_must_be_valid(cls, v):
        """Unit must be one of the accepted units."""
        if v not in VALID_UNITS:
            raise ValueError(f"Unit must be one of: {', '.join(VALID_UNITS)}")
        return v

    @field_validator("category")
    @classmethod
    def category_must_be_valid(cls, v):
        """Category must be one of the accepted categories."""
        if v not in VALID_CATEGORIES:
            raise ValueError(f"Category must be one of: {', '.join(VALID_CATEGORIES)}")
        return v


class ProductUpdate(BaseModel):
    """Data that can be updated in a product listing."""
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    unit: Optional[str] = None
    quantity_available: Optional[float] = None
    min_order_quantity: Optional[float] = None
    is_available: Optional[bool] = None

    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Price must be greater than zero")
        return v

    @field_validator("quantity_available")
    @classmethod
    def quantity_must_not_be_negative(cls, v):
        if v is not None and v < 0:
            raise ValueError("Quantity cannot be negative")
        return v


class ProductResponse(BaseModel):
    """Data we send back about a product."""
    id: int
    farmer_id: int
    name: str
    description: Optional[str] = None
    category: str
    price: float
    unit: str
    quantity_available: float
    min_order_quantity: float
    is_available: bool
    image: Optional[str] = None
    created_at: Optional[datetime] = None
    # Farmer info for display
    farmer_name: Optional[str] = None
    farmer_city: Optional[str] = None

    class Config:
        from_attributes = True
