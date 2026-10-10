import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Navbar from './components/Navbar';
import Marketplace from './pages/Marketplace';
import Cart from './pages/Cart';
import FarmerDashboard from './pages/FarmerDashboard';
import BuyerOrders from './pages/BuyerOrders';
import LogisticsDashboard from './pages/LogisticsDashboard';
import AIForecasting from './pages/AIForecasting';
import MandiRates from './pages/MandiRates';
import AdminDashboard from './pages/AdminDashboard';
import Login from './pages/Login';
import Register from './pages/Register';

// Protected Route wrapper checking roles
const ProtectedRoute = ({ children, allowedRoles }) => {
  const { user } = useAuth();
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <Navigate to="/" replace />;
  }
  return children;
};

function AppRoutes() {
  return (
    <div className="app-layout">
      <Navbar />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<Marketplace />} />
          <Route path="/cart" element={<Cart />} />
          <Route path="/mandi-rates" element={<MandiRates />} />
          <Route path="/forecasts" element={<AIForecasting />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Farmer Portal */}
          <Route
            path="/farmer-dashboard"
            element={
              <ProtectedRoute allowedRoles={['farmer', 'admin']}>
                <FarmerDashboard />
              </ProtectedRoute>
            }
          />

          {/* Buyer Orders */}
          <Route
            path="/buyer-orders"
            element={
              <ProtectedRoute allowedRoles={['consumer', 'bulk_buyer', 'admin']}>
                <BuyerOrders />
              </ProtectedRoute>
            }
          />

          {/* Logistics & Route Optimizer */}
          <Route
            path="/logistics"
            element={
              <ProtectedRoute allowedRoles={['logistics', 'admin']}>
                <LogisticsDashboard />
              </ProtectedRoute>
            }
          />

          {/* Platform Administrator */}
          <Route
            path="/admin"
            element={
              <ProtectedRoute allowedRoles={['admin']}>
                <AdminDashboard />
              </ProtectedRoute>
            }
          />

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>

      <footer className="platform-footer">
        <div className="footer-content">
          <p>
            🌾 <strong>KisanDirect Marketplace</strong> — AI-Powered Direct Farmer-to-Consumer Platform
          </p>
          <p className="footer-sub">
            Built for Hackathon Demonstration • Real Database Transactions • Zero Middleman Margins • Verified Local AI Models
          </p>
        </div>
      </footer>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </AuthProvider>
  );
}
