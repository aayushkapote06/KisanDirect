"""
main.py - The Main Application Entry Point

This is the heart of the backend. It:
1. Creates the FastAPI application
2. Sets up CORS (so the frontend can talk to the backend)
3. Creates all database tables
4. Includes all the API routers
5. Creates a default admin account (for local development only)

When you run "uvicorn app.main:app", this file is loaded first.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base, SessionLocal
from app.models import User, Product, Order, OrderItem, Delivery
from app.routers import auth, products, orders, admin, logistics, forecasts, mandi
from app.services.auth import hash_password

# Create the FastAPI application
app = FastAPI(
    title="Farmer Marketplace API",
    description="AI-Powered Direct Farmer-to-Consumer Digital Marketplace",
    version="1.0.0",
)

# ----- CORS MIDDLEWARE -----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----- INCLUDE ROUTERS -----
# Each router handles a group of related endpoints
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(admin.router)
app.include_router(logistics.router)
app.include_router(forecasts.router)
app.include_router(mandi.router)


# ----- STARTUP EVENT -----
@app.on_event("startup")
def on_startup():
    """
    This runs when the server starts.
    
    It creates all database tables (if they don't exist yet)
    and creates a default admin account for local development.
    """
    # Create all tables in the database
    Base.metadata.create_all(bind=engine)
    
    # Create default admin account (LOCAL DEVELOPMENT ONLY)
    # In production, you would create admin accounts through a secure process
    db = SessionLocal()
    try:
        existing_admin = db.query(User).filter(User.email == "admin@marketplace.com").first()
        if not existing_admin:
            admin_user = User(
                email="admin@marketplace.com",
                hashed_password=hash_password("admin123"),
                full_name="Platform Administrator",
                role="admin",
                is_active=True,
            )
            db.add(admin_user)
            db.commit()
            print("[OK] Default admin account created: admin@marketplace.com / admin123")
            print("[WARNING] Change this password in production!")
        else:
            print("[INFO] Admin account already exists.")
    finally:
        db.close()


# ----- ROOT ENDPOINT -----
@app.get("/")
def root():
    """A simple endpoint to verify the API is running."""
    return {
        "message": "🌾 Farmer Marketplace API is running!",
        "docs": "Visit /docs for interactive API documentation",
        "version": "1.0.0",
    }


@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
