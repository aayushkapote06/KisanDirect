"""
seed.py - Marketplace Database Seeder with Produce Images and Pulses

Populates authentic agricultural produce with high-quality imagery:
- Vegetables, Fruits, Grains, Pulses (Dal), Oilseeds, Spices, Dairy
- High-resolution curated agricultural produce images
- Verified farmers across regional production hubs
- Realistic prices in INR and realistic unit metrics (kg, quintal)
"""

from app.database import engine, Base, SessionLocal
from app.models import User, Product, Order, OrderItem, Delivery
from app.services.auth import hash_password


def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    print("[SEED] Resetting and updating marketplace catalog...")

    # 1. Admin Account
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
            "full_name": "Gurpreet Singh (Punjab Golden Harvest)",
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
            "full_name": "Suresh Patel (Maharashtra Agro Co-op)",
            "phone": "+91 94220 98765",
            "role": "farmer",
            "city": "Nashik",
            "state": "Maharashtra",
            "address": "Lasalgaon Mandi Sector",
            "latitude": "19.9975",
            "longitude": "73.7898",
        },
        {
            "email": "rajesh_mp@marketplace.com",
            "password": "farmerpassword123",
            "full_name": "Rajesh Malviya (Malwa Pulses Producer Co.)",
            "phone": "+91 97555 43210",
            "role": "farmer",
            "city": "Indore",
            "state": "Madhya Pradesh",
            "address": "Sanwer Agriculture Belt",
            "latitude": "22.7196",
            "longitude": "75.8577",
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

    db.commit()

    # 5. Expanded Agricultural Catalog with Direct Images
    catalog = [
        # --- VEGETABLES ---
        {
            "farmer_idx": 0,
            "name": "Farm-Fresh Desi Hybrid Tomatoes",
            "description": "Sun-ripened, naturally grown firm red tomatoes. Freshly plucked every morning, ideal for curries, salads, and puree.",
            "category": "Vegetables",
            "price": 28.0,
            "unit": "kg",
            "quantity_available": 850.0,
            "min_order_quantity": 5.0,
            "image": "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=600&auto=format&fit=crop&q=80",
        },
        {
            "farmer_idx": 2,
            "name": "Nashik Red Export Onions",
            "description": "Medium-to-large size pungent red onions with tight skins, cured naturally for longer shelf life. Direct from Lasalgaon.",
            "category": "Vegetables",
            "price": 32.0,
            "unit": "kg",
            "quantity_available": 2500.0,
            "min_order_quantity": 10.0,
            "image": "https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?w=600&auto=format&fit=crop&q=80",
        },
        {
            "farmer_idx": 0,
            "name": "Kufri Jyoti Fresh Farm Potatoes",
            "description": "Low-sugar, golden-skin table potatoes. Unwashed for maximum freshness and extended storage life.",
            "category": "Vegetables",
            "price": 22.0,
            "unit": "kg",
            "quantity_available": 3200.0,
            "min_order_quantity": 10.0,
            "image": "https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=600&auto=format&fit=crop&q=80",
        },
        {
            "farmer_idx": 0,
            "name": "Tender Green Ladyfinger (Bhindi)",
            "description": "Crisp, pesticide-free small okra plucked tender. High dietary fiber and zero seed hardness.",
            "category": "Vegetables",
            "price": 45.0,
            "unit": "kg",
            "quantity_available": 320.0,
            "min_order_quantity": 2.0,
            "image": "https://images.unsplash.com/photo-1604908177453-7462950a6a3b?w=600&auto=format&fit=crop&q=80",
        },
        {
            "farmer_idx": 1,
            "name": "Organic Farm Spinach (Palak)",
            "description": "Dark green broad-leaf spinach, harvested with root soil. Rich in iron and grown with vermicompost.",
            "category": "Vegetables",
            "price": 30.0,
            "unit": "kg",
            "quantity_available": 280.0,
            "min_order_quantity": 3.0,
            "image": "https://images.unsplash.com/photo-1576045057995-568f588f82fb?w=600&auto=format&fit=crop&q=80",
        },

        # --- PULSES (DALS & LEGUMES) ---
        {
            "farmer_idx": 3,
            "name": "Organic Unpolished Toor Dal (Arhar)",
            "description": "Pure unpolished pigeon pea dal from Madhya Pradesh. Free from artificial water or oil polishing; preserves natural protein.",
            "category": "Pulses",
            "price": 145.0,
            "unit": "kg",
            "quantity_available": 1200.0,
            "min_order_quantity": 5.0,
            "image": "https://images.unsplash.com/photo-1585994192701-f1a505c817ea?w=600&auto=format&fit=crop&q=80",
        },
        {
            "farmer_idx": 3,
            "name": "Desi Chana Whole (Bengal Gram)",
            "description": "Brown nutrient-dense whole chickpeas from Malwa region. High fiber and rich earthy aroma when cooked.",
            "category": "Pulses",
            "price": 85.0,
            "unit": "kg",
            "quantity_available": 1800.0,
            "min_order_quantity": 10.0,
            "image": "https://images.unsplash.com/photo-1515543237350-b3eea1ec8082?w=600&auto=format&fit=crop&q=80",
        },
        {
            "farmer_idx": 3,
            "name": "Green Moong Dal (Split Chilka)",
            "description": "Fresh harvest split green gram with peel. Light on digestion, unadulterated directly from FPO collection center.",
            "category": "Pulses",
            "price": 120.0,
            "unit": "kg",
            "quantity_available": 900.0,
            "min_order_quantity": 5.0,
            "image": "https://images.unsplash.com/photo-1610450919844-4b533318b76c?w=600&auto=format&fit=crop&q=80",
        },
        {
            "farmer_idx": 1,
            "name": "Kashmiri Red Rajma (Kidney Beans)",
            "description": "Small-grain authentic Kashmiri red kidney beans. Melts soft when boiled with distinct rich gravy flavor.",
            "category": "Pulses",
            "price": 160.0,
            "unit": "kg",
            "quantity_available": 750.0,
            "min_order_quantity": 5.0,
            "image": "https://images.unsplash.com/photo-1551462147-37885acc36f1?w=600&auto=format&fit=crop&q=80",
        },
        {
            "farmer_idx": 3,
            "name": "Organic Black Urad Whole (Sabut)",
            "description": "Whole black gram grain, perfect for Dal Makhani and traditional fermentation. Rich in calcium and iron.",
            "category": "Pulses",
            "price": 115.0,
            "unit": "kg",
            "quantity_available": 1100.0,
            "min_order_quantity": 5.0,
            "image": "https://images.unsplash.com/photo-1596797038530-2c107229654b?w=600&auto=format&fit=crop&q=80",
        },

        # --- FRUITS ---
        {
            "farmer_idx": 2,
            "name": "Mahabaleshwar Fresh Strawberries",
            "description": "Sweet, fragrant hand-plucked strawberries in ventilated cartons. Directly air-cooled post picking.",
            "category": "Fruits",
            "price": 190.0,
            "unit": "kg",
            "quantity_available": 180.0,
            "min_order_quantity": 2.0,
            "image": "https://images.unsplash.com/photo-1464965911861-746a04b4bca6?w=600&auto=format&fit=crop&q=80",
        },
        {
            "farmer_idx": 2,
            "name": "Ratnagiri Alphonso Mangoes (GI Tagged)",
            "description": "Naturally tree-ripened Alphonso (Hapus) mangoes with no chemical carbide ripening. Saffron pulp and heavenly aroma.",
            "category": "Fruits",
            "price": 450.0,
            "unit": "dozen",
            "quantity_available": 250.0,
            "min_order_quantity": 2.0,
            "image": "https://images.unsplash.com/photo-1553279768-865429fa0078?w=600&auto=format&fit=crop&q=80",
        },
        {
            "farmer_idx": 1,
            "name": "Kashmiri Royal Delicious Apples",
            "description": "Crisp, sweet red highland apples from Shopian valley. High juice retention and natural wax protection.",
            "category": "Fruits",
            "price": 140.0,
            "unit": "kg",
            "quantity_available": 850.0,
            "min_order_quantity": 5.0,
            "image": "https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=600&auto=format&fit=crop&q=80",
        },
        {
            "farmer_idx": 1,
            "name": "Fresh Kinnow Mandarins (Punjab)",
            "description": "Juicy sweet citrus mandarins directly from Abohar orchards. High Vitamin C content, excellent for fresh juice.",
            "category": "Fruits",
            "price": 55.0,
            "unit": "kg",
            "quantity_available": 1400.0,
            "min_order_quantity": 10.0,
            "image": "https://images.unsplash.com/photo-1611080626919-7cf5a9dbab5b?w=600&auto=format&fit=crop&q=80",
        },

        # --- GRAINS ---
        {
            "farmer_idx": 0,
            "name": "Traditional Basmati Paddy (Aromatic 1121)",
            "description": "Export grade, aged 1 year, extra-long grain aromatic basmati paddy harvested in Karnal belt.",
            "category": "Grains",
            "price": 82.0,
            "unit": "kg",
            "quantity_available": 3500.0,
            "min_order_quantity": 25.0,
            "image": "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=600&auto=format&fit=crop&q=80",
        },
        {
            "farmer_idx": 1,
            "name": "Sharbati Golden Whole Wheat",
            "description": "Heavy golden grains of famous Sharbati wheat. Yields exceptionally soft and sweet rotis with high water absorption.",
            "category": "Grains",
            "price": 34.0,
            "unit": "kg",
            "quantity_available": 5000.0,
            "min_order_quantity": 50.0,
            "image": "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=600&auto=format&fit=crop&q=80",
        },
        {
            "farmer_idx": 0,
            "name": "Organic Pearl Millet (Desi Bajra)",
            "description": "Drought-resilient traditional super-millet. Rich in iron, zinc, and dietary fiber; staple for healthy winter flour.",
            "category": "Grains",
            "price": 38.0,
            "unit": "kg",
            "quantity_available": 1200.0,
            "min_order_quantity": 20.0,
            "image": "https://images.unsplash.com/photo-1586201375761-83865001e31c?w=600&auto=format&fit=crop&q=80",
        },

        # --- OILSEEDS & SPICES ---
        {
            "farmer_idx": 1,
            "name": "Yellow Mustard Seeds (Pili Sarson)",
            "description": "Bold yellow mustard seeds with over 42% natural oil content. Cleaned mechanically with zero stones.",
            "category": "Oilseeds",
            "price": 72.0,
            "unit": "kg",
            "quantity_available": 600.0,
            "min_order_quantity": 10.0,
            "image": "https://images.unsplash.com/photo-1509358271058-acd22cc93898?w=600&auto=format&fit=crop&q=80",
        },
        {
            "farmer_idx": 2,
            "name": "Salem Pure Turmeric Fingers (Haldi)",
            "description": "High curcumin (4.5%+) unpolished whole turmeric fingers. Sun-dried in traditional raised beds.",
            "category": "Spices",
            "price": 130.0,
            "unit": "kg",
            "quantity_available": 450.0,
            "min_order_quantity": 5.0,
            "image": "https://images.unsplash.com/photo-1615485290382-441e4d049cb5?w=600&auto=format&fit=crop&q=80",
        },

        # --- DAIRY ---
        {
            "farmer_idx": 0,
            "name": "A2 Desi Gir Cow Vedic Bilona Ghee",
            "description": "Traditional curd-churned golden Bilona ghee made from grass-fed indigenous Gir cows. Granular texture and pure aroma.",
            "category": "Dairy",
            "price": 950.0,
            "unit": "litre",
            "quantity_available": 120.0,
            "min_order_quantity": 1.0,
            "image": "https://images.unsplash.com/photo-1628088062854-d1870b4553da?w=600&auto=format&fit=crop&q=80",
        },
    ]

    for p_info in catalog:
        farmer_obj = farmers[p_info["farmer_idx"]]
        existing_p = db.query(Product).filter(
            Product.farmer_id == farmer_obj.id,
            Product.name == p_info["name"]
        ).first()

        if existing_p:
            existing_p.image = p_info["image"]
            existing_p.description = p_info["description"]
            existing_p.category = p_info["category"]
            existing_p.price = p_info["price"]
            existing_p.unit = p_info["unit"]
            existing_p.quantity_available = p_info["quantity_available"]
            existing_p.min_order_quantity = p_info["min_order_quantity"]
            existing_p.is_available = True
        else:
            new_p = Product(
                farmer_id=farmer_obj.id,
                name=p_info["name"],
                description=p_info["description"],
                category=p_info["category"],
                price=p_info["price"],
                unit=p_info["unit"],
                quantity_available=p_info["quantity_available"],
                min_order_quantity=p_info["min_order_quantity"],
                image=p_info["image"],
                is_available=True,
            )
            db.add(new_p)

    db.commit()
    db.close()
    print(f"[SEED] Successfully seeded {len(catalog)} diverse agricultural items with images & pulses!")


if __name__ == "__main__":
    seed_database()
