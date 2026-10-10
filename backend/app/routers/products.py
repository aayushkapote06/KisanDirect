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
    # Determine appropriate produce image
    image_url = None
    lower_name = product_data.name.lower()
    keyword_map = {
        "paddy": "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=600&auto=format&fit=crop&q=80",
        "rice": "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=600&auto=format&fit=crop&q=80",
        "wheat": "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=600&auto=format&fit=crop&q=80",
        "tomato": "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=600&auto=format&fit=crop&q=80",
        "onion": "https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?w=600&auto=format&fit=crop&q=80",
        "potato": "https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=600&auto=format&fit=crop&q=80",
        "strawberry": "https://images.unsplash.com/photo-1464965911861-746a04b4bca6?w=600&auto=format&fit=crop&q=80",
        "mango": "https://images.unsplash.com/photo-1553279768-865429fa0078?w=600&auto=format&fit=crop&q=80",
        "apple": "https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=600&auto=format&fit=crop&q=80",
        "dal": "https://images.unsplash.com/photo-1585994192701-f1a505c817ea?w=600&auto=format&fit=crop&q=80",
        "chana": "https://images.unsplash.com/photo-1515543237350-b3eea1ec8082?w=600&auto=format&fit=crop&q=80",
        "rajma": "https://images.unsplash.com/photo-1551462147-37885acc36f1?w=600&auto=format&fit=crop&q=80",
        "moong": "https://images.unsplash.com/photo-1610450919844-4b533318b76c?w=600&auto=format&fit=crop&q=80",
        "mustard": "https://images.unsplash.com/photo-1509358271058-acd22cc93898?w=600&auto=format&fit=crop&q=80",
        "ghee": "https://images.unsplash.com/photo-1628088062854-d1870b4553da?w=600&auto=format&fit=crop&q=80",
    }
    category_defaults = {
        "Grains": "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=600&auto=format&fit=crop&q=80",
        "Vegetables": "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=600&auto=format&fit=crop&q=80",
        "Fruits": "https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=600&auto=format&fit=crop&q=80",
        "Pulses": "https://images.unsplash.com/photo-1585994192701-f1a505c817ea?w=600&auto=format&fit=crop&q=80",
        "Oilseeds": "https://images.unsplash.com/photo-1509358271058-acd22cc93898?w=600&auto=format&fit=crop&q=80",
        "Spices": "https://images.unsplash.com/photo-1615485290382-441e4d049cb5?w=600&auto=format&fit=crop&q=80",
        "Dairy": "https://images.unsplash.com/photo-1628088062854-d1870b4553da?w=600&auto=format&fit=crop&q=80",
    }
    for kw, url in keyword_map.items():
        if kw in lower_name:
            image_url = url
            break
    if not image_url:
        image_url = category_defaults.get(product_data.category, category_defaults["Vegetables"])

    new_product = Product(
        farmer_id=current_user.id,
        name=product_data.name,
        description=product_data.description,
        category=product_data.category,
        price=product_data.price,
        unit=product_data.unit,
        quantity_available=product_data.quantity_available,
        min_order_quantity=product_data.min_order_quantity,
        image=image_url,
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
    current_user: User = Depends(require_role(["farmer", "admin"])),
    db: Session = Depends(get_db),
):
    """
    Delete a product listing.
    - Farmer can delete their OWN listed products.
    - Administrator can delete ANY product on the platform.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found."
        )
    
    # Check permissions: Admin can delete any product, Farmer can only delete their own
    if current_user.role != "admin" and product.farmer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own products."
        )
    
    db.delete(product)
    db.commit()
