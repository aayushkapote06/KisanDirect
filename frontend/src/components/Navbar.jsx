import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { ShoppingCart, LogOut, User, Sprout, TrendingUp, Truck, ShieldCheck, Package } from 'lucide-react';

export default function Navbar() {
  const { user, cart, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const totalCartItems = cart.reduce((sum, item) => sum + item.quantity, 0);

  return (
    <header className="navbar-container">
      <div className="navbar-brand">
        <Link to="/" className="brand-logo">
          <Sprout className="logo-icon" size={28} />
          <span>KisanDirect</span>
        </Link>
        <span className="brand-tagline">Direct Farmer-to-Consumer</span>
      </div>

      <nav className="navbar-links">
        <Link to="/" className="nav-link">Marketplace</Link>
        <Link to="/forecasts" className="nav-link">
          <TrendingUp size={16} /> AI Demand Forecast
        </Link>

        {user && user.role === 'farmer' && (
          <Link to="/farmer-dashboard" className="nav-link highlight">
            <Sprout size={16} /> Farmer Dashboard
          </Link>
        )}

        {user && (user.role === 'consumer' || user.role === 'bulk_buyer') && (
          <Link to="/buyer-orders" className="nav-link">
            <Package size={16} /> My Orders
          </Link>
        )}

        {user && (user.role === 'logistics' || user.role === 'admin') && (
          <Link to="/logistics" className="nav-link">
            <Truck size={16} /> Logistics & Routes
          </Link>
        )}

        {user && user.role === 'admin' && (
          <Link to="/admin" className="nav-link admin-pill">
            <ShieldCheck size={16} /> Admin Panel
          </Link>
        )}
      </nav>

      <div className="navbar-actions">
        {(!user || user.role === 'consumer' || user.role === 'bulk_buyer') && (
          <Link to="/cart" className="cart-btn" title="View Cart">
            <ShoppingCart size={20} />
            {totalCartItems > 0 && <span className="cart-badge">{totalCartItems}</span>}
          </Link>
        )}

        {user ? (
          <div className="user-profile-menu">
            <div className="user-badge">
              <User size={16} />
              <div className="user-info">
                <span className="user-name">{user.full_name}</span>
                <span className={`role-tag role-${user.role}`}>{user.role.replace('_', ' ')}</span>
              </div>
            </div>
            <button onClick={handleLogout} className="btn-logout" title="Sign out">
              <LogOut size={18} />
            </button>
          </div>
        ) : (
          <div className="auth-buttons">
            <Link to="/login" className="btn btn-outline">Log In</Link>
            <Link to="/register" className="btn btn-primary">Register</Link>
          </div>
        )}
      </div>
    </header>
  );
}
