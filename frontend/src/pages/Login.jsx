import React, { useState } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Sprout, LogIn, AlertCircle, Sparkles } from 'lucide-react';

export default function Login() {
  const { login, loading } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const redirectPath = new URLSearchParams(location.search).get('redirect') || '/';

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setError('');
      const loggedUser = await login(email, password);
      // Route smartly based on role
      if (redirectPath && redirectPath !== '/') {
        navigate(redirectPath);
      } else if (loggedUser.role === 'farmer') {
        navigate('/farmer-dashboard');
      } else if (loggedUser.role === 'logistics') {
        navigate('/logistics');
      } else if (loggedUser.role === 'admin') {
        navigate('/admin');
      } else {
        navigate('/');
      }
    } catch (err) {
      setError(err.message || 'Invalid email or password.');
    }
  };

  // Quick Demo Login helper for hackathon evaluation
  const handleQuickDemo = (demoEmail, demoPass) => {
    setEmail(demoEmail);
    setPassword(demoPass);
  };

  return (
    <div className="auth-page-container">
      <div className="auth-card">
        <div className="auth-header">
          <Sprout className="logo-icon large" size={36} />
          <h2>Welcome Back to KisanDirect</h2>
          <p>Login to access direct farm trading, logistics, or platform analytics.</p>
        </div>

        {error && (
          <div className="alert-banner alert-error">
            <AlertCircle size={18} />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label>Email Address</label>
            <input
              type="email"
              required
              placeholder="name@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              required
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary btn-block"
            disabled={loading}
          >
            {loading ? 'Authenticating...' : (
              <>Sign In <LogIn size={18} /></>
            )}
          </button>
        </form>

        {/* 1-Click Quick Demo Accounts (Hackathon Evaluator Friendly) */}
        <div className="demo-credentials-box">
          <div className="demo-title">
            <Sparkles size={16} /> <strong>1-Click Demo Profiles (For Testing):</strong>
          </div>
          <div className="demo-btn-group">
            <button
              type="button"
              className="btn-demo-pill"
              onClick={() => handleQuickDemo('testfarmer@marketplace.com', 'farmerpassword123')}
            >
              🧑‍🌾 Farmer Demo
            </button>
            <button
              type="button"
              className="btn-demo-pill"
              onClick={() => handleQuickDemo('testconsumer@marketplace.com', 'consumerpassword123')}
            >
              🛒 Consumer Demo
            </button>
            <button
              type="button"
              className="btn-demo-pill"
              onClick={() => handleQuickDemo('admin@marketplace.com', 'admin123')}
            >
              🛡️ Admin Demo
            </button>
          </div>
        </div>

        <div className="auth-footer">
          Don't have an account yet? <Link to="/register">Register here</Link>
        </div>
      </div>
    </div>
  );
}
