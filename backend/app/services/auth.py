"""
services/auth.py - Authentication Service

This file handles:
1. Password hashing - converting "mypassword123" into an unreadable string
2. Password verification - checking if a password matches its hash
3. JWT token creation - creating a "login pass" that proves who you are
4. JWT token verification - checking if a login pass is valid

SECURITY CONCEPTS:
- We NEVER store passwords as plain text. We "hash" them - a one-way transformation.
  Even if someone steals the database, they can't read the passwords.
- JWT (JSON Web Token) is like a temporary ID card. After you log in,
  we give you a token. You send this token with every request to prove who you are.
- Tokens expire after a set time (30 minutes by default), so stolen tokens
  become useless quickly.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User

# ----- PASSWORD HASHING -----

# This creates a password hasher using the "bcrypt" algorithm
# bcrypt is slow on purpose - it makes brute-force attacks impractical
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Convert a plain text password into a hashed version."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check if a plain text password matches its hashed version."""
    return pwd_context.verify(plain_password, hashed_password)


# ----- JWT TOKEN HANDLING -----

# SECRET_KEY is used to sign tokens. In production, this should be a long
# random string stored in an environment variable. For our local MVP,
# we use a hardcoded key. NEVER use this in production!
SECRET_KEY = "farmer-marketplace-dev-secret-key-change-in-production-2024"
ALGORITHM = "HS256"  # The signing algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = 120  # Token valid for 2 hours


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT token.
    
    The token contains:
    - "sub" (subject): the user's email
    - "role": the user's role
    - "user_id": the user's database ID
    - "exp": when the token expires
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# ----- GETTING THE CURRENT USER FROM A TOKEN -----

# This tells FastAPI: "Look for a token in the Authorization header"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Extract the current user from the JWT token.
    
    This function is used as a "dependency" in API endpoints.
    When an endpoint needs to know who's making the request,
    it calls this function, which:
    1. Reads the token from the request header
    2. Decodes it
    3. Finds the user in the database
    4. Returns the user object
    
    If the token is missing, expired, or invalid, it raises an error.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials. Please log in again.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Find the user in the database
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account has been deactivated. Contact administrator."
        )
    
    return user


def require_role(allowed_roles: list):
    """
    Create a dependency that checks if the current user has the required role.
    
    Usage in an endpoint:
        @router.get("/admin-only")
        def admin_endpoint(user = Depends(require_role(["admin"]))):
            ...
    
    This ensures that only users with the "admin" role can access this endpoint.
    If a consumer tries to access it, they get a 403 Forbidden error.
    """
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {', '.join(allowed_roles)}. Your role: {current_user.role}"
            )
        return current_user
    return role_checker
