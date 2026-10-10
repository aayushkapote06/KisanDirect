import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { api } from '../api';
import { ShoppingCart, Trash2, ArrowRight, ShieldCheck, AlertCircle } from 'lucide-react';

export default function Cart() {
  const { user, cart, updateCartQuantity, removeFromCart, clearCart } = useAuth();
  const navigate = useNavigate();

  const [address, setAddress] = useState(user?.address || '');
  const [city, setCity] = useState(user?.city || 'Delhi');
  const [pincode, setPincode] = useState(user?.pincode || '110001');
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const subtotal = cart.reduce((sum, item) => sum + item.product.price * item.quantity, 0);

  const handleCheckout = async (e) => {
    e.preventDefault();
    if (!user) {
      navigate('/login?redirect=/cart');
      return;
    }

    if (cart.length === 0) {
      setError('Your shopping cart is empty.');
      return;
    }

    if (!address.trim()) {
      setError('Please provide a delivery address.');
      return;
    }

    try {
      setLoading(true);
      setError('');

      const orderPayload = {
        items: cart.map((item) => ({
          product_id: item.product.id,
          quantity: item.quantity,
        })),
        delivery_address: address,
        delivery_city: city,
        delivery_pincode: pincode,
        notes: notes || undefined,
      };

      const result = await api.createOrder(orderPayload);
      clearCart();
      navigate('/buyer-orders', { state: { newOrderId: result.id } });
    } catch (err) {
      setError(err.message || 'Failed to place order.');
    } finally {
      setLoading(false);
    }
  };

  if (cart.length === 0) {
    return (
      <div className="page-container empty-cart-view">
        <ShoppingCart size={64} className="muted-icon" />
        <h2>Your Cart is Empty</h2>
        <p>Explore fresh agricultural produce listed directly by verified farmers.</p>
        <Link to="/" className="btn btn-primary">Browse Marketplace</Link>
      </div>
    );
  }

  return (
    <div className="page-container cart-page">
      <h1>Review Direct Farm Order</h1>
      <p className="page-subtitle">All proceeds go directly to farmers. Zero intermediaries.</p>

      {error && (
        <div className="alert-banner alert-error">
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      <div className="cart-layout">
        {/* Cart Items List */}
        <div className="cart-items-section">
          <h3>Items in Order ({cart.length})</h3>
          <div className="cart-items-list">
            {cart.map((item) => (
              <div key={item.product.id} className="cart-item-row">
                <div className="cart-item-info">
                  <h4>{item.product.name}</h4>
                  <span className="cart-item-farmer">Sold by: {item.product.farmer_name || 'Direct Farmer'}</span>
                  <span className="cart-item-rate">₹{item.product.price} / {item.product.unit}</span>
                </div>

                <div className="cart-item-qty">
                  <label>Qty ({item.product.unit}):</label>
                  <input
                    type="number"
                    min="1"
                    max={item.product.quantity_available}
                    value={item.quantity}
                    onChange={(e) => updateCartQuantity(item.product.id, Number(e.target.value))}
                  />
                </div>

                <div className="cart-item-total">
                  ₹{(item.product.price * item.quantity).toFixed(2)}
                </div>

                <button
                  className="btn-icon-danger"
                  onClick={() => removeFromCart(item.product.id)}
                  title="Remove item"
                >
                  <Trash2 size={18} />
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Checkout Form & Summary */}
        <div className="cart-summary-section">
          <div className="summary-card">
            <h3>Order Summary</h3>
            <div className="summary-line">
              <span>Produce Subtotal:</span>
              <span className="summary-val">₹{subtotal.toFixed(2)}</span>
            </div>
            <div className="summary-line">
              <span>Middleman Commission:</span>
              <span className="summary-val green-text">₹0.00 (Saved!)</span>
            </div>
            <div className="summary-line">
              <span>Simulated Logistics:</span>
              <span className="summary-val">₹0.00 (Demo Tier)</span>
            </div>
            <hr />
            <div className="summary-line total-line">
              <span>Total Payable to Farmers:</span>
              <span className="total-amount">₹{subtotal.toFixed(2)}</span>
            </div>

            <form onSubmit={handleCheckout} className="checkout-address-form">
              <h4>Delivery Details</h4>
              <div className="form-group">
                <label>Delivery Address *</label>
                <input
                  type="text"
                  required
                  placeholder="Street address / Mandi / Shop number"
                  value={address}
                  onChange={(e) => setAddress(e.target.value)}
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>City / Town</label>
                  <input
                    type="text"
                    required
                    value={city}
                    onChange={(e) => setCity(e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label>Pincode</label>
                  <input
                    type="text"
                    required
                    value={pincode}
                    onChange={(e) => setPincode(e.target.value)}
                  />
                </div>
              </div>

              <div className="form-group">
                <label>Special Instructions (Optional)</label>
                <input
                  type="text"
                  placeholder="e.g. Unloading bay details, contact on arrival"
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                />
              </div>

              <div className="simulated-payment-notice">
                <ShieldCheck size={16} />
                <span>Simulated Demo Payment: No real money will be charged during hackathon evaluation.</span>
              </div>

              <button
                type="submit"
                className="btn btn-primary btn-block"
                disabled={loading}
              >
                {loading ? 'Processing Order...' : (
                  <>Place Direct Order <ArrowRight size={18} /></>
                )}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
