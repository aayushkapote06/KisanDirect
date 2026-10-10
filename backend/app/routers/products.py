"""
routers/products.py - Product API Endpoints

This file defines the API endpoints for:
- GET    /api/products          → List all available products (any user)
- GET    /api/products/{id}     → Get a single product's details
- POST   /api/products          → Add a new product (farmer only)
- PUT    /api/products/{id}     → Update a product (owner farmer only)
- DELETE /api/products/{id}     → Delete a product (owner farmer only)
- GET    /api/products/farmer/me → Get current farmer's own products
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.database import get_db
from app.models.user import User
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.services.auth import get_current_user, require_role

router = APIRouter(prefix="/api/products", tags=["Products"])


@router.get("", response_model=List[ProductResponse])
def list_products(
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search by product name"),
    min_price: Optional[float] = Query(None, description="Minimum price"),
    max_price: Optional[float] = Query(None, description="Maximum price"),
    db: Session = Depends(get_db),
):
    """
    List all available products. Anyone can view products.
    
    Supports filtering by:
    - category (e.g., "Vegetables")
    - search (product name contains this text)
    - min_price and max_price (price range)
    """
    query = db.query(Product).filter(Product.is_available == True)
    
    if category:
        query = query.filter(Product.category == category)
    
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
    
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    products = query.order_by(Product.created_at.desc()).all()
    
    # Add farmer info to each product
    result = []
    for product in products:
        farmer = db.query(User).filter(User.id == product.farmer_id).first()
        product_data = ProductResponse.model_validate(product)
        product_data.farmer_name = farmer.full_name if farmer else "Unknown"
        product_data.farmer_city = farmer.city if farmer else None
        result.append(product_data)
    
    return result


@router.get("/farmer/me", response_model=List[ProductResponse])
def get_my_products(
    current_user: User = Depends(require_role(["farmer"])),
    db: Session = Depends(get_db),
):
    """Get all products listed by the currently logged-in farmer."""
    products = db.query(Product).filter(
        Product.farmer_id == current_user.id
    ).order_by(Product.created_at.desc()).all()
    
    result = []
    for product in products:
        product_data = ProductResponse.model_validate(product)
        product_data.farmer_name = current_user.full_name
        product_data.farmer_city = current_user.city
        result.append(product_data)
    
    return result


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get details of a single product by its ID."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found."
        )
    
    farmer = db.query(User).filter(User.id == product.farmer_id).first()
    product_data = ProductResponse.model_validate(product)
    product_data.farmer_name = farmer.full_name if farmer else "Unknown"
    product_data.farmer_city = farmer.city if farmer else None
    
    return product_data


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product_data: ProductCreate,
    current_user: User = Depends(require_role(["farmer"])),
    db: Session = Depends(get_db),
):
    """
    Add a new product listing. Only farmers can do this.
    
    The farmer_id is automatically set to the logged-in farmer's ID.
    A farmer cannot list products under another farmer's name.
    """
    new_product = Product(
        farmer_id=current_user.id,
        name=product_data.name,
        description=product_data.description,
        category=product_data.category,
        price=product_data.price,
        unit=product_data.unit,
        quantity_available=product_data.quantity_available,
        min_order_quantity=product_data.min_order_quantity,
    )
    
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    product_response = ProductResponse.model_validate(new_product)
    product_response.farmer_name = current_user.full_name
    product_response.farmer_city = current_user.city
    
    return product_response


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    current_user: User = Depends(require_role(["farmer"])),
    db: Session = Depends(get_db),
):
    """
    Update a product listing. Only the farmer who owns it can update it.
    
    SECURITY: We check that the logged-in farmer is the owner of this product.
    A farmer cannot edit another farmer's products.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found."
        )
    
    # SECURITY CHECK: Only the owner can update
    if product.farmer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own products."
        )
    
    # Update only the fields that were provided
    update_data = product_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)
    
    db.commit()
    db.refresh(product)
    
    product_response = ProductResponse.model_validate(product)
    product_response.farmer_name = current_user.full_name
    product_response.farmer_city = current_user.city
    
    return product_response


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    current_user: User = Depends(require_role(["farmer"])),
    db: Session = Depends(get_db),
):
    """
    Delete a product listing. Only the farmer who owns it can delete it.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found."
        )
    
    if product.farmer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own products."
        )
    
    db.delete(product)
    db.commit()
