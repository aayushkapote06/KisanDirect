"""
tests/test_api.py - Backend Test Suite

Tests all core backend functionalities:
1. Health check
2. Registration and login authentication
3. Farmer product creation and discovery
4. Consumer ordering and server-side inventory decrement
5. AI Demand forecasting output and metrics
6. AI Route optimization calculations and savings
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_registration_and_login():
    # Register a new farmer
    farmer_data = {
        "email": "testfarmer@marketplace.com",
        "password": "farmerpassword123",
        "full_name": "Ramesh Kumar",
        "phone": "+919876543210",
        "role": "farmer",
        "city": "Karnal",
        "state": "Haryana",
    }
    # Might already exist if re-running, so accept 201 or 400
    reg_resp = client.post("/api/auth/register", json=farmer_data)
    assert reg_resp.status_code in [201, 400]

    # Login
    login_resp = client.post(
        "/api/auth/login",
        json={"email": farmer_data["email"], "password": farmer_data["password"]},
    )
    assert login_resp.status_code == 200
    data = login_resp.json()
    assert "access_token" in data
    assert data["role"] == "farmer"


def test_product_creation_and_listing():
    # Login as farmer
    login_resp = client.post(
        "/api/auth/login",
        json={"email": "testfarmer@marketplace.com", "password": "farmerpassword123"},
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create product
    prod_data = {
        "name": "Fresh Organic Basmati Paddy",
        "description": "Naturally grown aromatic long-grain paddy",
        "category": "Grains",
        "price": 65.0,
        "unit": "kg",
        "quantity_available": 500.0,
        "min_order_quantity": 10.0,
    }
    create_resp = client.post("/api/products", json=prod_data, headers=headers)
    assert create_resp.status_code == 201
    product = create_resp.json()
    assert product["name"] == prod_data["name"]
    assert product["price"] == 65.0

    # Public listing
    list_resp = client.get("/api/products")
    assert list_resp.status_code == 200
    products = list_resp.json()
    assert any(p["id"] == product["id"] for p in products)


def test_order_creation_and_inventory_decrement():
    # Register & Login consumer
    consumer_data = {
        "email": "testconsumer@marketplace.com",
        "password": "consumerpassword123",
        "full_name": "Pooja Sharma",
        "role": "consumer",
        "city": "Delhi",
    }
    client.post("/api/auth/register", json=consumer_data)
    login_resp = client.post(
        "/api/auth/login",
        json={"email": consumer_data["email"], "password": consumer_data["password"]},
    )
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Find the product
    products = client.get("/api/products").json()
    assert len(products) > 0
    target_prod = products[0]
    initial_qty = target_prod["quantity_available"]
    order_qty = 10.0

    # Place order
    order_payload = {
        "items": [{"product_id": target_prod["id"], "quantity": order_qty}],
        "delivery_address": "12 Connaught Place, New Delhi",
        "delivery_city": "Delhi",
    }
    order_resp = client.post("/api/orders", json=order_payload, headers=headers)
    assert order_resp.status_code == 201
    order = order_resp.json()
    assert order["status"] == "placed"
    assert order["total_amount"] == round(target_prod["price"] * order_qty, 2)

    # Verify inventory was decremented
    updated_prod = client.get(f"/api/products/{target_prod['id']}").json()
    assert updated_prod["quantity_available"] == initial_qty - order_qty


def test_ai_demand_forecasting():
    resp = client.get("/api/forecasts/demand?crop=Tomatoes&months=4")
    assert resp.status_code == 200
    data = resp.json()
    assert data["crop_name"] == "Tomatoes"
    assert len(data["forecast"]) == 4
    assert "metrics" in data
    assert "mae_demand_kg" in data["metrics"]
    assert "farmer_recommendation" in data


def test_route_optimization():
    payload = {
        "depot": {"name": "Karnal Farm Depot", "address": "Karnal", "lat": 29.6857, "lng": 76.9905},
        "stops": [
            {"name": "Delhi Mandi", "address": "Azadpur", "lat": 28.7126, "lng": 77.1755, "order_id": 1},
            {"name": "Gurugram Hub", "address": "Sector 29", "lat": 28.4682, "lng": 77.0635, "order_id": 2},
            {"name": "Sonipat Center", "address": "Sonipat Road", "lat": 28.9931, "lng": 77.0151, "order_id": 3},
        ],
    }
    resp = client.post("/api/logistics/route-optimize", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "optimized_distance_km" in data
    assert "distance_saved_km" in data
    assert data["distance_saved_km"] > 0
    assert len(data["optimized_stops"]) == 4  # depot + 3 stops
