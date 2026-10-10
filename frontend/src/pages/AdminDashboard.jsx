import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { useAuth } from '../context/AuthContext';
import { ShieldCheck, Users, ShoppingCart, DollarSign, UserCheck, UserX, AlertCircle, CheckCircle2, Trash2, Package } from 'lucide-react';

export default function AdminDashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [orders, setOrders] = useState([]);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  const loadAdminData = async () => {
    try {
      setLoading(true);
      setError('');
      const [statsData, usersData, ordersData, productsData] = await Promise.all([
        api.getAdminStats(),
        api.getAdminUsers(),
        api.getAdminOrders(),
        api.getProducts(),
      ]);
      setStats(statsData);
      setUsers(usersData);
      setOrders(ordersData);
      setProducts(productsData);
    } catch (err) {
      setError(err.message || 'Failed to load administrative data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAdminData();
  }, []);

  const handleToggleUser = async (userId, currentActive, name) => {
    const action = currentActive ? 'deactivate' : 'activate';
    if (!window.confirm(`Are you sure you want to ${action} user "${name}"?`)) return;

    try {
      setError('');
      const res = await api.toggleUserActive(userId);
      setSuccessMsg(res.message);
      loadAdminData();
      setTimeout(() => setSuccessMsg(''), 4000);
    } catch (err) {
      setError(err.message || 'Failed to toggle user status');
    }
  };

  const handleAdminDeleteProduct = async (productId, productName, farmerName) => {
    if (!window.confirm(`[ADMIN ACTION] Are you sure you want to permanently delete listing "${productName}" by ${farmerName}?`)) return;

    try {
      setError('');
      await api.deleteProduct(productId);
      setSuccessMsg(`[Admin] Successfully removed "${productName}" from the platform.`);
      loadAdminData();
      setTimeout(() => setSuccessMsg(''), 4000);
    } catch (err) {
      setError(err.message || 'Failed to delete product');
    }
  };

  return (
    <div className="page-container">
      <div className="dashboard-header">
        <div>
          <h1>Platform Administration</h1>
          <p className="page-subtitle">
            System governance, multi-role user management, catalog moderation, and transaction monitoring.
          </p>
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

      {/* KPI Cards */}
      {stats && (
        <div className="stats-cards-grid">
          <div className="dashboard-stat-card">
            <span className="stat-label">Total Registered Users</span>
            <span className="stat-number">{stats.users.total}</span>
            <span className="stat-sub">
              {stats.users.farmers} Farmers | {stats.users.consumers} Consumers | {stats.users.bulk_buyers} Bulk Buyers
            </span>
          </div>

          <div className="dashboard-stat-card">
            <span className="stat-label">Total Platform Orders</span>
            <span className="stat-number">{stats.orders.total}</span>
            <span className="stat-sub">{stats.orders.pending} pending fulfillment</span>
          </div>

          <div className="dashboard-stat-card">
            <span className="stat-label">Total Delivered Turnover</span>
            <span className="stat-number green-text">₹{stats.revenue.total_delivered.toFixed(2)}</span>
            <span className="stat-sub">Zero platform cut, 100% farmer paid</span>
          </div>

          <div className="dashboard-stat-card">
            <span className="stat-label">Available Product Listings</span>
            <span className="stat-number">{stats.products.available}</span>
            <span className="stat-sub">Out of {stats.products.total} total catalog items</span>
          </div>
        </div>
      )}

      {/* Product Catalog Moderation Table */}
      <div className="card dashboard-table-card">
        <h3>Product Catalog Moderation & Removal ({products.length} Items Listed)</h3>
        <p className="page-subtitle" style={{ marginBottom: '1rem' }}>
          Administrators have global authority to remove fraudulent, out-of-stock, or policy-violating listings.
        </p>
        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th>Item ID</th>
                <th>Produce Name</th>
                <th>Category</th>
                <th>Listed by Farmer</th>
                <th>Price</th>
                <th>Available Qty</th>
                <th>Status</th>
                <th>Admin Action</th>
              </tr>
            </thead>
            <tbody>
              {products.map((p) => (
                <tr key={p.id}>
                  <td>#{p.id}</td>
                  <td><strong>{p.name}</strong></td>
                  <td><span className="badge">{p.category}</span></td>
                  <td>
                    <span>{p.farmer_name || 'Farmer'}</span>
                    {p.farmer_city && <span className="stop-addr">📍 {p.farmer_city}</span>}
                  </td>
                  <td>₹{p.price} / {p.unit}</td>
                  <td>{p.quantity_available} {p.unit}</td>
                  <td>
                    <span className={`badge ${p.is_available ? 'badge-success' : 'badge-danger'}`}>
                      {p.is_available ? 'Available' : 'Unavailable'}
                    </span>
                  </td>
                  <td>
                    <button
                      onClick={() => handleAdminDeleteProduct(p.id, p.name, p.farmer_name)}
                      className="btn btn-sm btn-danger-outline"
                      title="Permanently remove listing from marketplace"
                    >
                      <Trash2 size={14} /> Remove Item
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* User Management Table */}
      <div className="card dashboard-table-card">
        <h3>User Management & Moderation ({users.length})</h3>
        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th>User ID</th>
                <th>Full Name</th>
                <th>Email Address</th>
                <th>Role</th>
                <th>City / Region</th>
                <th>Status</th>
                <th>Admin Action</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id}>
                  <td>#{u.id}</td>
                  <td><strong>{u.full_name}</strong></td>
                  <td>{u.email}</td>
                  <td>
                    <span className={`role-tag role-${u.role}`}>{u.role.replace('_', ' ')}</span>
                  </td>
                  <td>{u.city || 'N/A'}</td>
                  <td>
                    <span className={`badge ${u.is_active ? 'badge-success' : 'badge-danger'}`}>
                      {u.is_active ? 'Active' : 'Suspended'}
                    </span>
                  </td>
                  <td>
                    {u.id === user.id ? (
                      <span className="text-muted">(Current Admin)</span>
                    ) : (
                      <button
                        onClick={() => handleToggleUser(u.id, u.is_active, u.full_name)}
                        className={`btn btn-sm ${u.is_active ? 'btn-danger-outline' : 'btn-success-outline'}`}
                      >
                        {u.is_active ? <UserX size={14} /> : <UserCheck size={14} />}
                        {u.is_active ? ' Suspend' : ' Activate'}
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Recent Orders Overview */}
      <div className="card dashboard-table-card">
        <h3>Platform Order Audit Log ({orders.length})</h3>
        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th>Order ID</th>
                <th>Buyer</th>
                <th>Items Count</th>
                <th>Total Value</th>
                <th>Delivery Destination</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {orders.map((o) => (
                <tr key={o.id}>
                  <td>#{o.id}</td>
                  <td>{o.buyer_name || `Buyer #${o.buyer_id}`}</td>
                  <td>{o.items?.length || 0} items</td>
                  <td><strong>₹{o.total_amount.toFixed(2)}</strong></td>
                  <td>{o.delivery_city || o.delivery_address || 'Standard'}</td>
                  <td>
                    <span className={`status-pill status-${o.status}`}>
                      {o.status.toUpperCase()}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
