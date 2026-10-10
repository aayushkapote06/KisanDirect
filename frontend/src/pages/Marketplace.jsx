import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { useAuth } from '../context/AuthContext';
import { Search, Filter, ShoppingBag, CheckCircle, Info, ShieldAlert, Sprout } from 'lucide-react';

const CATEGORIES = [
  'All', 'Vegetables', 'Pulses', 'Fruits', 'Grains', 'Oilseeds', 'Spices', 'Dairy'
];

export default function Marketplace() {
  const { user, addToCart } = useAuth();
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [quantities, setQuantities] = useState({});
  const [addedNotice, setAddedNotice] = useState('');

  const fetchProducts = async () => {
    try {
      setLoading(true);
      setError('');
      const params = {};
      if (selectedCategory !== 'All') params.category = selectedCategory;
      if (search.trim()) params.search = search.trim();

      const data = await api.getProducts(params);
      setProducts(data);
    } catch (err) {
      setError(err.message || 'Failed to load products');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, [selectedCategory]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchProducts();
  };

  const handleQuantityChange = (productId, val, maxVal) => {
    const parsed = Math.max(1, Math.min(Number(val) || 1, maxVal));
    setQuantities((prev) => ({ ...prev, [productId]: parsed }));
  };

  const handleAddToCart = (product) => {
    const qty = quantities[product.id] || product.min_order_quantity || 1;
    addToCart(product, qty);
    setAddedNotice(`Added ${qty} ${product.unit} of "${product.name}" to cart!`);
    setTimeout(() => setAddedNotice(''), 3000);
  };

  return (
    <div className="page-container">
      {/* Hero Banner */}
      <section className="hero-banner">
        <div className="hero-content">
          <h1>Direct From Farm to Your Doorstep</h1>
          <p>
            Zero unnecessary middlemen. 100% fair prices for farmers and transparent savings for consumers & bulk buyers.
          </p>
        </div>
        <div className="hero-stats">
          <div className="stat-card">
            <span className="stat-num">₹0</span>
            <span className="stat-label">Middleman Commission</span>
          </div>
          <div className="stat-card">
            <span className="stat-num">100%</span>
            <span className="stat-label">Direct Farmer Settlement</span>
          </div>
          <div className="stat-card">
            <span className="stat-num">AI</span>
            <span className="stat-label">Route & Demand Optimized</span>
          </div>
        </div>
      </section>

      {/* Notice alert */}
      {addedNotice && (
        <div className="alert-banner alert-success">
          <CheckCircle size={18} />
          <span>{addedNotice}</span>
        </div>
      )}

      {error && (
        <div className="alert-banner alert-error">
          <ShieldAlert size={18} />
          <span>{error}</span>
        </div>
      )}

      {/* Search and Category Filters */}
      <div className="marketplace-controls">
        <form onSubmit={handleSearchSubmit} className="search-bar">
          <Search size={18} className="search-icon" />
          <input
            type="text"
            placeholder="Search fresh produce (e.g. Tomatoes, Basmati Rice, Toor Dal, Strawberries)..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <button type="submit" className="btn btn-primary">Search</button>
        </form>

        <div className="category-chips">
          {CATEGORIES.map((cat) => (
            <button
              key={cat}
              className={`chip ${selectedCategory === cat ? 'chip-active' : ''}`}
              onClick={() => setSelectedCategory(cat)}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Product Grid */}
      {loading ? (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Connecting to farmer inventories...</p>
        </div>
      ) : products.length === 0 ? (
        <div className="empty-state">
          <ShoppingBag size={48} />
          <h3>No products found</h3>
          <p>Try adjusting your search query or category filter.</p>
        </div>
      ) : (
        <div className="product-grid">
          {products.map((prod) => {
            const currentQty = quantities[prod.id] || prod.min_order_quantity || 1;
            const canBuy = !user || user.role === 'consumer' || user.role === 'bulk_buyer';

            return (
              <div key={prod.id} className="product-card">
                {/* Produce Photo Banner */}
                <div className="product-image-container">
                  {prod.image ? (
                    <img
                      src={prod.image}
                      alt={prod.name}
                      className="product-img"
                      loading="lazy"
                      onError={(e) => {
                        e.target.style.display = 'none';
                        const fallback = e.target.parentElement.querySelector('.product-img-fallback');
                        if (fallback) fallback.style.display = 'flex';
                      }}
                    />
                  ) : null}
                  <div className="product-img-fallback" style={{ display: prod.image ? 'none' : 'flex' }}>
                    <Sprout size={36} />
                  </div>
                  <span className="product-category-tag-floating">{prod.category}</span>
                </div>

                <div className="product-body">
                  <h3 className="product-title">{prod.name}</h3>
                  <p className="product-description">{prod.description || 'Freshly harvested produce directly from the farm.'}</p>

                  <div className="product-farmer-meta">
                    <span className="farmer-badge">🧑‍🌾 Farmer: {prod.farmer_name || 'Verified Farmer'}</span>
                    {prod.farmer_city && <span className="farmer-location">📍 {prod.farmer_city}</span>}
                  </div>

                  <div className="product-pricing">
                    <div className="price-box">
                      <span className="currency">₹</span>
                      <span className="amount">{prod.price}</span>
                      <span className="unit">/{prod.unit}</span>
                    </div>
                    <div className="stock-box">
                      <span className="stock-label">Available:</span>
                      <span className="stock-qty">{prod.quantity_available} {prod.unit}</span>
                    </div>
                  </div>

                  {prod.min_order_quantity > 1 && (
                    <div className="min-order-pill">
                      Min order: {prod.min_order_quantity} {prod.unit}
                    </div>
                  )}

                  {canBuy ? (
                    <div className="product-actions">
                      <div className="qty-picker">
                        <label>Qty:</label>
                        <input
                          type="number"
                          min={prod.min_order_quantity}
                          max={prod.quantity_available}
                          step={prod.unit === 'tonne' || prod.unit === 'quintal' ? 0.5 : 1}
                          value={currentQty}
                          onChange={(e) => handleQuantityChange(prod.id, e.target.value, prod.quantity_available)}
                        />
                        <span className="unit-label">{prod.unit}</span>
                      </div>
                      <button
                        className="btn btn-primary btn-add-cart"
                        onClick={() => handleAddToCart(prod)}
                        disabled={prod.quantity_available <= 0}
                      >
                        {prod.quantity_available > 0 ? 'Add to Cart' : 'Out of Stock'}
                      </button>
                    </div>
                  ) : (
                    <div className="role-restriction-note">
                      <Info size={14} /> Logged in as {user.role}. Sign in as Buyer to purchase.
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
