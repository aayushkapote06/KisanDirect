import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { useAuth } from '../context/AuthContext';
import { useLocation, Link } from 'react-router-dom';
import { Package, Clock, CheckCircle, Ban, AlertCircle, ShoppingBag } from 'lucide-react';

export default function BuyerOrders() {
  const { user } = useAuth();
  const location = useLocation();
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState(
    location.state?.newOrderId ? `Order #${location.state.newOrderId} successfully placed!` : ''
  );

  const fetchOrders = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await api.getMyOrders();
      setOrders(data);
    } catch (err) {
      setError(err.message || 'Failed to fetch order history');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrders();
  }, []);

  const handleCancelOrder = async (orderId) => {
    if (!window.confirm(`Are you sure you want to cancel Order #${orderId}? Stock will be returned to the farmer.`)) return;
    try {
      await api.updateOrderStatus(orderId, 'cancelled');
      setSuccessMsg(`Order #${orderId} was cancelled.`);
      fetchOrders();
      setTimeout(() => setSuccessMsg(''), 4000);
    } catch (err) {
      setError(err.message || 'Could not cancel order.');
    }
  };

  return (
    <div className="page-container">
      <div className="dashboard-header">
        <div>
          <h1>My Orders & Purchases</h1>
          <p className="page-subtitle">Track your direct orders from farmers and check delivery status.</p>
        </div>
        <Link to="/" className="btn btn-outline">
          <ShoppingBag size={16} /> Continue Shopping
        </Link>
      </div>

      {successMsg && (
        <div className="alert-banner alert-success">
          <CheckCircle size={18} />
          <span>{successMsg}</span>
        </div>
      )}

      {error && (
        <div className="alert-banner alert-error">
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      {loading ? (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading your orders...</p>
        </div>
      ) : orders.length === 0 ? (
        <div className="empty-state card">
          <Package size={54} className="muted-icon" />
          <h3>No Orders Placed Yet</h3>
          <p>You haven't placed any farm orders yet. Support local farmers and order fresh produce today.</p>
          <Link to="/" className="btn btn-primary">Go to Marketplace</Link>
        </div>
      ) : (
        <div className="orders-stack">
          {orders.map((order) => {
            const canCancel = order.status === 'placed' || order.status === 'confirmed';

            return (
              <div key={order.id} className="card order-card">
                <div className="order-card-header">
                  <div>
                    <span className="order-num">Order #{order.id}</span>
                    <span className="order-date">
                      {order.created_at ? new Date(order.created_at).toLocaleDateString() : 'Recent'}
                    </span>
                  </div>
                  <div className="order-status-group">
                    <span className={`status-pill status-${order.status}`}>
                      {order.status.toUpperCase()}
                    </span>
                    {canCancel && (
                      <button
                        onClick={() => handleCancelOrder(order.id)}
                        className="btn btn-sm btn-outline btn-danger"
                      >
                        <Ban size={14} /> Cancel
                      </button>
                    )}
                  </div>
                </div>

                <div className="order-items-table">
                  {order.items.map((item) => (
                    <div key={item.id} className="order-item-detail">
                      <div>
                        <strong>{item.product_name}</strong>
                        <span className="item-meta">Sold by Farmer: {item.farmer_name}</span>
                      </div>
                      <div className="item-rate">
                        {item.quantity} units × ₹{item.unit_price}
                      </div>
                      <div className="item-subtotal">
                        ₹{item.total_price.toFixed(2)}
                      </div>
                    </div>
                  ))}
                </div>

                <div className="order-card-footer">
                  <div className="delivery-info">
                    <strong>Delivery Destination:</strong>
                    <span>{order.delivery_address || 'Address provided during order'}</span>
                    {order.delivery_city && <span>, {order.delivery_city} ({order.delivery_pincode})</span>}
                  </div>
                  <div className="total-badge">
                    <span>Total Amount:</span>
                    <strong>₹{order.total_amount.toFixed(2)}</strong>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
