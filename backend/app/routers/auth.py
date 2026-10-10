"""
routers/auth.py - Authentication API Endpoints

This file defines the API endpoints for:
- POST /api/auth/register  → Create a new account
- POST /api/auth/login     → Log in and get a token
- GET  /api/auth/me        → Get current user's profile

API ENDPOINT EXPLAINED:
An "endpoint" is a URL that your application responds to.
When the frontend sends a request to "/api/auth/register" with
a user's name, email, and password, this code processes it,
creates the account, and sends back a response.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.services.auth import (
    hash_password, verify_password, create_access_token, get_current_user
)

# Create a "router" - a group of related endpoints
router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# Valid roles that users can register as
ALLOWED_REGISTRATION_ROLES = ["farmer", "consumer", "bulk_buyer", "logistics"]


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    
    What happens:
    1. Check if the email is already taken
    2. Validate the role
    3. Hash the password
    4. Save the user to the database
    5. Return the user's info (without the password!)
    """
    
    # 1. Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists."
        )
    
    # 2. Validate role - users cannot register as "admin"
    if user_data.role not in ALLOWED_REGISTRATION_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(ALLOWED_REGISTRATION_ROLES)}"
        )
    
    # 3. Create the user with a hashed password
    new_user = User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
        phone=user_data.phone,
        role=user_data.role,
        address=user_data.address,
        city=user_data.city,
        state=user_data.state,
        pincode=user_data.pincode,
        latitude=user_data.latitude,
        longitude=user_data.longitude,
    )
    
    # 4. Save to database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # Reload from DB to get the auto-generated id and timestamps
    
    return new_user


@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    Log in and receive a JWT token.
    
    What happens:
    1. Find the user by email
    2. Verify the password
    3. Create a JWT token
    4. Return the token
    """
    
    # 1. Find user by email
    user = db.query(User).filter(User.email == user_data.email).first()
    
    # 2. Check if user exists and password is correct
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. Check if account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account has been deactivated. Contact administrator."
        )
    
    # 4. Create and return the token
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role, "user_id": user.id}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role,
        "user_id": user.id,
        "full_name": user.full_name,
    }


@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_user)):
    """
    Get the currently logged-in user's profile.
    
    This endpoint requires a valid JWT token.
    The get_current_user dependency extracts the user from the token.
    """
    return current_user
