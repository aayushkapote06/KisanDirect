import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { useAuth } from '../context/AuthContext';
import { Link } from 'react-router-dom';
import { PlusCircle, Trash2, Sprout, TrendingUp, PackageCheck, AlertCircle, CheckCircle2 } from 'lucide-react';

const CATEGORIES = [
  'Vegetables', 'Grains', 'Fruits', 'Pulses', 'Spices', 'Dairy', 'Oilseeds', 'Other'
];

const UNITS = ['kg', 'quintal', 'tonne', 'piece', 'dozen', 'litre'];

export default function FarmerDashboard() {
  const { user } = useAuth();
  const [products, setProducts] = useState([]);
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  // Add Product Form State
  const [showAddForm, setShowAddForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    category: 'Vegetables',
    price: '',
    unit: 'kg',
    quantity_available: '',
    min_order_quantity: '1',
    description: '',
  });

  const loadData = async () => {
    try {
      setLoading(true);
      setError('');
      const [prods, ords] = await Promise.all([
        api.getFarmerProducts(),
        api.getFarmerOrders(),
      ]);
      setProducts(prods);
      setOrders(ords);
    } catch (err) {
      setError(err.message || 'Failed to load farmer dashboard');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleAddProduct = async (e) => {
    e.preventDefault();
    try {
      setError('');
      await api.createProduct({
        ...formData,
        price: parseFloat(formData.price),
        quantity_available: parseFloat(formData.quantity_available),
        min_order_quantity: parseFloat(formData.min_order_quantity) || 1,
      });
      setSuccessMsg(`"${formData.name}" successfully listed for sale!`);
      setFormData({
        name: '',
        category: 'Vegetables',
        price: '',
        unit: 'kg',
        quantity_available: '',
        min_order_quantity: '1',
        description: '',
      });
      setShowAddForm(false);
      loadData();
      setTimeout(() => setSuccessMsg(''), 4000);
    } catch (err) {
      setError(err.message || 'Failed to add product');
    }
  };

  const handleDeleteProduct = async (id, name) => {
    if (!window.confirm(`Are you sure you want to remove listing "${name}"?`)) return;
    try {
      await api.deleteProduct(id);
      setProducts((prev) => prev.filter((p) => p.id !== id));
      setSuccessMsg(`Listing "${name}" removed.`);
      setTimeout(() => setSuccessMsg(''), 3000);
    } catch (err) {
      setError(err.message || 'Failed to delete product');
    }
  };

  const handleUpdateOrderStatus = async (orderId, newStatus) => {
    try {
      await api.updateOrderStatus(orderId, newStatus);
      setSuccessMsg(`Order #${orderId} updated to ${newStatus}`);
      loadData();
      setTimeout(() => setSuccessMsg(''), 3000);
    } catch (err) {
      setError(err.message || 'Failed to update order status');
    }
  };

  // Financial calculations
  const totalEarnings = orders
    .filter((o) => o.status === 'delivered')
    .reduce((sum, o) => sum + o.total_amount, 0);

  const pendingOrders = orders.filter((o) => o.status !== 'delivered' && o.status !== 'cancelled');

  return (
    <div className="page-container dashboard-page">
      <div className="dashboard-header">
        <div>
          <h1>Farmer Management Dashboard</h1>
          <p className="page-subtitle">Manage harvest listings, incoming buyer orders, and real-time revenue.</p>
        </div>
        <div className="dashboard-header-actions">
          <Link to="/forecasts" className="btn btn-outline">
            <TrendingUp size={16} /> Check Crop Demand AI
          </Link>
          <button
            onClick={() => setShowAddForm(!showAddForm)}
            className="btn btn-primary"
          >
            <PlusCircle size={18} /> {showAddForm ? 'Close Form' : 'List New Produce'}
          </button>
        </div>
      </div>

      {successMsg && (
        <div className="alert-banner alert-success">
          <CheckCircle2 size={18} />
          <span>{successMsg}</span>
        </div>
      )}

      {error && (
        <div className="alert-banner alert-error">
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      {/* KPI Overview Cards */}
      <div className="stats-cards-grid">
        <div className="dashboard-stat-card">
          <span className="stat-label">Delivered Revenue (Gross)</span>
          <span className="stat-number green-text">₹{totalEarnings.toFixed(2)}</span>
          <span className="stat-sub">100% direct settlement, 0% commission</span>
        </div>
        <div className="dashboard-stat-card">
          <span className="stat-label">Pending / Active Orders</span>
          <span className="stat-number">{pendingOrders.length}</span>
          <span className="stat-sub">Awaiting preparation & dispatch</span>
        </div>
        <div className="dashboard-stat-card">
          <span className="stat-label">Active Listed Produce</span>
          <span className="stat-number">{products.length}</span>
          <span className="stat-sub">Visible to consumers & bulk buyers</span>
        </div>
        <div className="dashboard-stat-card">
          <span className="stat-label">Total Orders Handled</span>
          <span className="stat-number">{orders.length}</span>
          <span className="stat-sub">All-time marketplace transactions</span>
        </div>
      </div>

      {/* Add Produce Form */}
      {showAddForm && (
        <div className="card add-produce-card">
          <h3>List Agricultural Produce</h3>
          <form onSubmit={handleAddProduct} className="form-grid">
            <div className="form-group">
              <label>Crop / Produce Name *</label>
              <input
                type="text"
                required
                placeholder="e.g. Sharbati Wheat, Hybrid Tomato"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
            </div>

            <div className="form-group">
              <label>Category *</label>
              <select
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
              >
                {CATEGORIES.map((cat) => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Selling Price (₹ per unit) *</label>
              <input
                type="number"
                step="0.5"
                min="1"
                required
                placeholder="e.g. 40"
                value={formData.price}
                onChange={(e) => setFormData({ ...formData, price: e.target.value })}
              />
            </div>

            <div className="form-group">
              <label>Measurement Unit *</label>
              <select
                value={formData.unit}
                onChange={(e) => setFormData({ ...formData, unit: e.target.value })}
              >
                {UNITS.map((u) => (
                  <option key={u} value={u}>{u}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Quantity Available for Sale *</label>
              <input
                type="number"
                step="1"
                min="1"
                required
                placeholder="e.g. 500"
                value={formData.quantity_available}
                onChange={(e) => setFormData({ ...formData, quantity_available: e.target.value })}
              />
            </div>

            <div className="form-group">
              <label>Minimum Order Quantity</label>
              <input
                type="number"
                step="1"
                min="1"
                placeholder="1"
                value={formData.min_order_quantity}
                onChange={(e) => setFormData({ ...formData, min_order_quantity: e.target.value })}
              />
            </div>

            <div className="form-group full-width">
              <label>Description & Harvest Details</label>
              <textarea
                rows="2"
                placeholder="Pesticide-free, organic harvested on Nov 10, grade A quality..."
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              />
            </div>

            <div className="form-actions full-width">
              <button type="submit" className="btn btn-primary">Publish Produce Listing</button>
              <button type="button" onClick={() => setShowAddForm(false)} className="btn btn-outline">Cancel</button>
            </div>
          </form>
        </div>
      )}

      {/* Produce Listings Table */}
      <div className="card dashboard-table-card">
        <h3>My Listed Produce ({products.length})</h3>
        {products.length === 0 ? (
          <p className="empty-hint">No produce listings yet. Click "List New Produce" above to start selling.</p>
        ) : (
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Produce</th>
                  <th>Category</th>
                  <th>Price</th>
                  <th>Available Stock</th>
                  <th>Min Order</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {products.map((p) => (
                  <tr key={p.id}>
                    <td><strong>{p.name}</strong></td>
                    <td><span className="badge">{p.category}</span></td>
                    <td>₹{p.price} / {p.unit}</td>
                    <td>{p.quantity_available} {p.unit}</td>
                    <td>{p.min_order_quantity} {p.unit}</td>
                    <td>
                      <span className={`badge ${p.is_available ? 'badge-success' : 'badge-danger'}`}>
                        {p.is_available ? 'In Stock' : 'Out of Stock'}
                      </span>
                    </td>
                    <td>
                      <button
                        onClick={() => handleDeleteProduct(p.id, p.name)}
                        className="btn btn-sm btn-danger-outline"
                        title="Remove listing from marketplace"
                      >
                        <Trash2 size={14} /> Remove Listing
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Orders for Farmer's Produce */}
      <div className="card dashboard-table-card">
        <h3>Incoming Orders for My Produce ({orders.length})</h3>
        {orders.length === 0 ? (
          <p className="empty-hint">No orders received yet. Orders placed by consumers will appear here in real-time.</p>
        ) : (
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Order #</th>
                  <th>Buyer</th>
                  <th>Items</th>
                  <th>Total Amount</th>
                  <th>Current Status</th>
                  <th>Update Workflow Status</th>
                </tr>
              </thead>
              <tbody>
                {orders.map((ord) => (
                  <tr key={ord.id}>
                    <td>#{ord.id}</td>
                    <td>{ord.buyer_name || 'Verified Buyer'}</td>
                    <td>
                      {ord.items.map((it) => (
                        <div key={it.id} className="order-sub-item">
                          {it.product_name}: {it.quantity} units @ ₹{it.unit_price}
                        </div>
                      ))}
                    </td>
                    <td><strong>₹{ord.total_amount.toFixed(2)}</strong></td>
                    <td>
                      <span className={`status-pill status-${ord.status}`}>{ord.status.toUpperCase()}</span>
                    </td>
                    <td>
                      <div className="status-action-btns">
                        {ord.status === 'placed' && (
                          <button
                            onClick={() => handleUpdateOrderStatus(ord.id, 'confirmed')}
                            className="btn btn-sm btn-primary"
                          >
                            Confirm Order
                          </button>
                        )}
                        {ord.status === 'confirmed' && (
                          <button
                            onClick={() => handleUpdateOrderStatus(ord.id, 'preparing')}
                            className="btn btn-sm btn-primary"
                          >
                            Mark Preparing
                          </button>
                        )}
                        {ord.status === 'preparing' && (
                          <button
                            onClick={() => handleUpdateOrderStatus(ord.id, 'dispatched')}
                            className="btn btn-sm btn-primary"
                          >
                            Mark Dispatched
                          </button>
                        )}
                        {ord.status === 'dispatched' && (
                          <span className="text-muted">In delivery by logistics</span>
                        )}
                        {ord.status === 'delivered' && (
                          <span className="green-text">✅ Completed & Settled</span>
                        )}
                        {ord.status === 'cancelled' && (
                          <span className="red-text">Cancelled</span>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
