import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Sprout, UserPlus, AlertCircle } from 'lucide-react';

const ROLES = [
  { value: 'farmer', label: 'Farmer / FPO (Produce Seller)', icon: '🧑‍🌾' },
  { value: 'consumer', label: 'Consumer (Household Buyer)', icon: '🛒' },
  { value: 'bulk_buyer', label: 'Bulk Buyer (Restaurant / Hotel / Trader)', icon: '🏢' },
  { value: 'logistics', label: 'Logistics / Fleet Provider', icon: '🚚' },
];

export default function Register() {
  const { register, loading } = useAuth();
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    email: '',
    password: '',
    full_name: '',
    phone: '',
    role: 'consumer',
    city: '',
    state: '',
    address: '',
    pincode: '',
  });

  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setError('');
      const loggedUser = await register(formData);
      if (loggedUser.role === 'farmer') {
        navigate('/farmer-dashboard');
      } else if (loggedUser.role === 'logistics') {
        navigate('/logistics');
      } else {
        navigate('/');
      }
    } catch (err) {
      setError(err.message || 'Registration failed.');
    }
  };

  return (
    <div className="auth-page-container">
      <div className="auth-card register-card">
        <div className="auth-header">
          <Sprout className="logo-icon large" size={36} />
          <h2>Join the Direct Farm Marketplace</h2>
          <p>Create your verified account in less than a minute.</p>
        </div>

        {error && (
          <div className="alert-banner alert-error">
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label>Select Your Platform Role *</label>
            <div className="role-selector-grid">
              {ROLES.map((r) => (
                <div
                  key={r.value}
                  className={`role-option-box ${formData.role === r.value ? 'selected' : ''}`}
                  onClick={() => setFormData({ ...formData, role: r.value })}
                >
                  <span className="role-icon">{r.icon}</span>
                  <div className="role-text-meta">
                    <strong>{r.label.split('(')[0]}</strong>
                    <span className="role-subtext">({r.label.split('(')[1]}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Full Name / Business Name *</label>
              <input
                type="text"
                required
                placeholder="e.g. Ramesh Singh / Green Valley Farm"
                value={formData.full_name}
                onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
              />
            </div>

            <div className="form-group">
              <label>Phone Number *</label>
              <input
                type="tel"
                required
                placeholder="+91 98765 43210"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Email Address *</label>
              <input
                type="email"
                required
                placeholder="name@example.com"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              />
            </div>

            <div className="form-group">
              <label>Password *</label>
              <input
                type="password"
                required
                placeholder="••••••••"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>City / Mandi / District *</label>
              <input
                type="text"
                required
                placeholder="e.g. Karnal"
                value={formData.city}
                onChange={(e) => setFormData({ ...formData, city: e.target.value })}
              />
            </div>

            <div className="form-group">
              <label>State *</label>
              <input
                type="text"
                required
                placeholder="e.g. Haryana"
                value={formData.state}
                onChange={(e) => setFormData({ ...formData, state: e.target.value })}
              />
            </div>

            <div className="form-group">
              <label>Pincode</label>
              <input
                type="text"
                placeholder="132001"
                value={formData.pincode}
                onChange={(e) => setFormData({ ...formData, pincode: e.target.value })}
              />
            </div>
          </div>

          <div className="form-group">
            <label>Farm / Delivery Address</label>
            <input
              type="text"
              placeholder="Village, Tehsil, or Street Location"
              value={formData.address}
              onChange={(e) => setFormData({ ...formData, address: e.target.value })}
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary btn-block"
            disabled={loading}
          >
            {loading ? 'Creating Account...' : (
              <>Complete Registration <UserPlus size={18} /></>
            )}
          </button>
        </form>

        <div className="auth-footer">
          Already registered? <Link to="/login">Sign in here</Link>
        </div>
      </div>
    </div>
  );
}
