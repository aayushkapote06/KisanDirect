# 🌾 KisanDirect: AI-Powered Direct Farmer-to-Consumer Digital Marketplace

> **Hackathon-Ready MVP**: A transparent digital marketplace that bridges farmers and Farmer Producer Organizations (FPOs) directly with consumers and bulk buyers, bypassing exploitative intermediaries, supporting agile logistics, and leveraging AI for demand forecasting and TSP 2-Opt delivery route optimization.

---

## 🚀 Key Highlights & Differentiators

1. **Zero Middlemen & Transparent Prices**: 100% of the produce purchase price flows directly to the farmer without intermediary cuts.
2. **Strict Server-Side Validation**: Product pricing, available inventories, and order subtotals are computed strictly on the backend to prevent frontend tampering or overselling.
3. **AI Demand & Price Forecasting**: Supervised Time-Series Seasonal Decomposition + Ordinary Least Squares (OLS) regression trained on agricultural cycles (Kharif, Rabi, Zaid) with transparent accuracy metrics (MAE, RMSE, %) and actionable harvesting recommendations.
4. **AI Route Optimization (TSP 2-Opt)**: Solves the multi-stop agricultural delivery problem using Haversine great-circle distance matrices and 2-Opt heuristic edge swapping. Quantifies exact kilometers and delivery minutes saved compared to baseline sequential routing.
5. **Multi-Role Access Control**: Role-based access control (RBAC) enforced on every API route for:
   - 🧑‍🌾 **Farmer / FPO**: Inventory listing, order dispatch workflow, revenue analytics
   - 🛒 **Consumer**: Produce discovery, search, filter, direct cart, order tracking
   - 🏢 **Bulk Buyer**: Large quantities, institutional ordering (restaurants/hotels)
   - 🚚 **Logistics Fleet**: Delivery assignment, status updates, AI route optimizer
   - 🛡️ **Administrator**: Platform governance, user moderation, order audit log

---

## 🏗️ System Architecture

```
[ React 18 + Vite Frontend ] (Port 5173)
         │
         │ REST API (JSON + Bearer JWT)
         ▼
[ FastAPI Backend (Python) ] (Port 8000)
    ├── Auth & Security (Bcrypt + JWT)
    ├── Catalog & Order Transactions (Atomic Inventory Reduction)
    ├── AI Demand Forecasting (Multiplicative Seasonality + Regression)
    └── AI Route Optimizer (Haversine + 2-Opt Heuristic)
         │
         │ SQLAlchemy ORM
         ▼
[ SQLite Database (marketplace.db) ]
```

---

## 🔑 Pre-Configured Demo Accounts (For Instant Evaluation)

You can log in instantly using the **1-Click Demo Buttons** on the Login page or use these credentials:

| Role | Email Address | Password | Intended Workflow |
|---|---|---|---|
| 🧑‍🌾 **Farmer** | `testfarmer@marketplace.com` | `farmerpassword123` | List produce, confirm/dispatch orders, check revenue |
| 🛒 **Consumer** | `testconsumer@marketplace.com` | `consumerpassword123` | Browse catalog, add to cart, order, track status |
| 🏢 **Bulk Buyer** | `hotelgrand@marketplace.com` | `buyerpassword123` | Place large-scale restaurant/hotel orders |
| 🚚 **Logistics** | `logistics@marketplace.com` | `driver123` | Accept deliveries, optimize multi-stop delivery routes |
| 🛡️ **Admin** | `admin@marketplace.com` | `admin123` | Audit platform orders, toggle user account active/suspended |

---

## 🛠️ How to Run the Application on Windows

### 1. Start the Backend (Terminal 1)
```powershell
cd D:\CEP\farmer-marketplace\backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```
- Interactive API Documentation: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Health Check: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

### 2. Start the Frontend (Terminal 2)
```powershell
cd D:\CEP\farmer-marketplace\frontend
npm run dev
```
- Open in your browser: [http://localhost:5173/](http://localhost:5173/)

### 3. Run Automated Tests
```powershell
cd D:\CEP\farmer-marketplace\backend
.\venv\Scripts\Activate.ps1
python -m pytest tests\test_api.py -v
```

---

## 🎯 5-Minute Hackathon Demonstration Script

Follow this script to deliver an end-to-end hackathon demonstration:

1. **The Problem & Marketplace (1 min)**:
   - Open [http://localhost:5173/](http://localhost:5173/).
   - Explain the core issue: traditional supply chains have 4-6 intermediaries taking 50-70% margins.
   - Show the live catalog: **Basmati Paddy**, **Desi Tomatoes**, **Sharbati Wheat**, etc. Notice farmer location tags and transparent unit rates (₹/kg, quintal).

2. **Consumer Buying & Direct Checkout (1 min)**:
   - Click "Log In" → Click **"🛒 Consumer Demo"** → Sign In.
   - Filter by "Vegetables", select 10 kg of Desi Tomatoes, and click "Add to Cart".
   - Go to Cart: notice the **₹0 Middleman Commission** breakdown. Enter delivery address and click **"Place Direct Order"**.
   - Show the Order History screen with order status: `PLACED`.

3. **Farmer Order Fulfillment & Earnings (1 min)**:
   - Log out → Click "Log In" → Click **"🧑‍🌾 Farmer Demo"**.
   - You are navigated to the **Farmer Dashboard**.
   - Show the real-time financial counter: Total Delivered Turnover, Active Harvest Listings.
   - Under "Incoming Orders", see the order placed by the consumer. Click **"Confirm Order"** → **"Mark Preparing"** → **"Mark Dispatched"**.
   - Show how stock automatically decremented on the marketplace to prevent overselling.

4. **AI Demand & Price Forecasting (1 min)**:
   - In the top navigation, click **"AI Demand Forecast"**.
   - Select **Tomatoes** and choose **Next 6 Months**.
   - Point out the **Model Accuracy Rating (97.7%)**, **Mean Absolute Error (MAE)** in kg, and the visual comparison bars between historical sales and predicted demand.
   - Highlight the **Actionable Farmer Decision Insight** advising farmers on peak market timing.

5. **Logistics & AI 2-Opt Route Optimization (1 min)**:
   - Navigate to **"Logistics & Routes"** (or log in as `logistics@marketplace.com`).
   - Show the multi-stop delivery batch starting from Karnal Farm Hub and delivering across Delhi-NCR.
   - Click **"Optimize Multi-Stop Route"**.
   - Watch the algorithm calculate the optimal TSP sequence: show the **28.5% Mileage Reduction**, **56.3 km saved**, and **96.5 minutes saved in delivery time**!

---

## 📈 Roadmap for Future Enhancements
- [ ] Integration with Government e-NAM (National Agriculture Market) price feeds.
- [ ] Real-time IoT sensor telemetry from cold-chain delivery trucks.
- [ ] Multilingual voice assistant for regional vernacular dialects.
- [ ] UPI QR payment gateway webhook integration.
