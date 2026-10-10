"""
seed.py - Marketplace Database Seeder

Populates realistic sample data for hackathon presentation:
- Verified Farmers across agricultural hubs (Haryana, Punjab, Maharashtra)
- Diverse Produce (Grains, Vegetables, Fruits, Oilseeds, Dairy) with real prices in INR
- Bulk Buyers and Consumers
- Logistics Fleet Providers
- Sample Orders and Deliveries with geographic coordinates
"""

from app.database import engine, Base, SessionLocal
from app.models import User, Product, Order, OrderItem, Delivery
from app.services.auth import hash_password


def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    print("[SEED] Starting database initialization...")

    # 1. Ensure Admin Account
    admin = db.query(User).filter(User.email == "admin@marketplace.com").first()
    if not admin:
        admin = User(
            email="admin@marketplace.com",
            hashed_password=hash_password("admin123"),
            full_name="Platform Administrator",
            role="admin",
            city="New Delhi",
            state="Delhi",
            is_active=True,
        )
        db.add(admin)

    # 2. Farmers
    farmers_data = [
        {
            "email": "testfarmer@marketplace.com",
            "password": "farmerpassword123",
            "full_name": "Ramesh Kumar (Karnal Organic FPO)",
            "phone": "+91 98120 44551",
            "role": "farmer",
            "city": "Karnal",
            "state": "Haryana",
            "address": "Village Taraori, Karnal Mandi Road",
            "latitude": "29.6857",
            "longitude": "76.9905",
        },
        {
            "email": "gurpreet@marketplace.com",
            "password": "farmerpassword123",
            "full_name": "Gurpreet Singh (Golden Wheat Farms)",
            "phone": "+91 98765 11223",
            "role": "farmer",
            "city": "Ludhiana",
            "state": "Punjab",
            "address": "Samrala Farm Estate",
            "latitude": "30.9010",
            "longitude": "75.8573",
        },
        {
            "email": "suresh@marketplace.com",
            "password": "farmerpassword123",
            "full_name": "Suresh Patel (Nashik Agro Co-op)",
            "phone": "+91 94220 98765",
            "role": "farmer",
            "city": "Nashik",
            "state": "Maharashtra",
            "address": "Lasalgaon Mandi Sector",
            "latitude": "19.9975",
            "longitude": "73.7898",
        },
    ]

    farmers = []
    for f_info in farmers_data:
        existing = db.query(User).filter(User.email == f_info["email"]).first()
        if not existing:
            u = User(
                email=f_info["email"],
                hashed_password=hash_password(f_info["password"]),
                full_name=f_info["full_name"],
                phone=f_info["phone"],
                role=f_info["role"],
                city=f_info["city"],
                state=f_info["state"],
                address=f_info["address"],
                latitude=f_info["latitude"],
                longitude=f_info["longitude"],
                is_active=True,
            )
            db.add(u)
            db.flush()
            farmers.append(u)
        else:
            farmers.append(existing)

    # 3. Buyers
    buyers_data = [
        {
            "email": "testconsumer@marketplace.com",
            "password": "consumerpassword123",
            "full_name": "Pooja Sharma (Household Consumer)",
            "phone": "+91 98111 22334",
            "role": "consumer",
            "city": "Delhi",
            "state": "Delhi",
            "address": "C-42, Hauz Khas, New Delhi",
            "latitude": "28.5494",
            "longitude": "77.2001",
        },
        {
            "email": "hotelgrand@marketplace.com",
            "password": "buyerpassword123",
            "full_name": "The Grand Horizon Hotel & Catering",
            "phone": "+91 99990 88776",
            "role": "bulk_buyer",
            "city": "Gurugram",
            "state": "Haryana",
            "address": "Sector 29 Commercial Hub",
            "latitude": "28.4682",
            "longitude": "77.0635",
        },
    ]

    buyers = []
    for b_info in buyers_data:
        existing = db.query(User).filter(User.email == b_info["email"]).first()
        if not existing:
            u = User(
                email=b_info["email"],
                hashed_password=hash_password(b_info["password"]),
                full_name=b_info["full_name"],
                phone=b_info["phone"],
                role=b_info["role"],
                city=b_info["city"],
                state=b_info["state"],
                address=b_info["address"],
                latitude=b_info["latitude"],
                longitude=b_info["longitude"],
                is_active=True,
            )
            db.add(u)
            db.flush()
            buyers.append(u)
        else:
            buyers.append(existing)

    # 4. Logistics Provider
    logistics_user = db.query(User).filter(User.email == "logistics@marketplace.com").first()
    if not logistics_user:
        logistics_user = User(
            email="logistics@marketplace.com",
            hashed_password=hash_password("driver123"),
            full_name="Kisan Express Fleet Logistics",
            phone="+91 98100 55667",
            role="logistics",
            city="New Delhi",
            state="Delhi",
            address="Azadpur Cold Storage Hub",
            latitude="28.7126",
            longitude="77.1755",
            is_active=True,
        )
        db.add(logistics_user)
        db.flush()

    # 5. Products Catalog
    products_catalog = [
        {
            "farmer": farmers[0],
            "name": "Traditional Basmati Paddy (Aromatic 1121)",
            "description": "Export grade, aged 1 year, zero moisture loss paddy directly from Karnal farm gates.",
            "category": "Grains",
            "price": 82.0,
            "unit": "kg",
            "quantity_available": 1500.0,
            "min_order_quantity": 25.0,
        },
        {
            "farmer": farmers[0],
            "name": "Farm-Fresh Desi Hybrid Tomatoes",
            "description": "Sun-ripened, firm tomatoes harvested daily morning. Ideal for daily retail and salads.",
            "category": "Vegetables",
            "price": 28.0,
            "unit": "kg",
            "quantity_available": 600.0,
            "min_order_quantity": 5.0,
        },
        {
            "farmer": farmers[1],
            "name": "Sharbati Golden Whole Wheat",
            "description": "High-protein premium whole wheat grain from the fertile soils of Ludhiana.",
            "category": "Grains",
            "price": 32.0,
            "unit": "kg",
            "quantity_available": 3000.0,
            "min_order_quantity": 50.0,
        },
        {
            "farmer": farmers[1],
            "name": "Yellow Mustard Seeds (Sarson)",
            "description": "High oil content, natural organic yellow mustard seeds for cold-press oil.",
            "category": "Oilseeds",
            "price": 68.0,
            "unit": "kg",
            "quantity_available": 450.0,
            "min_order_quantity": 10.0,
        },
        {
            "farmer": farmers[2],
            "name": "Nashik Red Export Onions",
            "description": "Medium-to-large size pungent red onions with extended shelf-life.",
            "category": "Vegetables",
            "price": 30.0,
            "unit": "kg",
            "quantity_available": 2200.0,
            "min_order_quantity": 20.0,
        },
        {
            "farmer": farmers[2],
            "name": "Mahabaleshwar Fresh Strawberries",
            "description": "Sweet, grade-A hand-picked strawberries in ventilated punnets.",
            "category": "Fruits",
            "price": 180.0,
            "unit": "kg",
            "quantity_available": 120.0,
            "min_order_quantity": 2.0,
        },
    ]

    for p_info in products_catalog:
        exists = db.query(Product).filter(
            Product.farmer_id == p_info["farmer"].id,
            Product.name == p_info["name"]
        ).first()
        if not exists:
            prod = Product(
                farmer_id=p_info["farmer"].id,
                name=p_info["name"],
                description=p_info["description"],
                category=p_info["category"],
                price=p_info["price"],
                unit=p_info["unit"],
                quantity_available=p_info["quantity_available"],
                min_order_quantity=p_info["min_order_quantity"],
                is_available=True,
            )
            db.add(prod)

    db.commit()

    # 6. Sample Initial Order & Delivery
    existing_order = db.query(Order).first()
    if not existing_order:
        p1 = db.query(Product).first()
        if p1 and len(buyers) > 1:
            bulk_buyer = buyers[1]
            order_amount = p1.price * 50.0
            order = Order(
                buyer_id=bulk_buyer.id,
                status="confirmed",
                total_amount=order_amount,
                delivery_address="Grand Horizon Hotel, Sector 29",
                delivery_city="Gurugram",
                delivery_pincode="122001",
                delivery_latitude="28.4682",
                delivery_longitude="77.0635",
                payment_status="paid",
                notes="Early morning delivery required before kitchen shifts.",
            )
            db.add(order)
            db.flush()

            order_item = OrderItem(
                order_id=order.id,
                product_id=p1.id,
                farmer_id=p1.farmer_id,
                quantity=50.0,
                unit_price=p1.price,
                total_price=order_amount,
                status="confirmed",
            )
            db.add(order_item)

            delivery = Delivery(
                order_id=order.id,
                logistics_provider_id=logistics_user.id,
                status="assigned",
                pickup_address="Karnal Farm Mandi Hub",
                pickup_latitude="29.6857",
                pickup_longitude="76.9905",
                delivery_address="Grand Horizon Hotel, Sector 29, Gurugram",
                delivery_latitude="28.4682",
                delivery_longitude="77.0635",
                estimated_distance_km=138.5,
                estimated_time_minutes=230.0,
            )
            db.add(delivery)
            db.commit()

    db.close()
    print("[SEED] Successfully seeded farmers, produce catalogs, buyers, and logistics!")


if __name__ == "__main__":
    seed_database()
