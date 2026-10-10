import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { useAuth } from '../context/AuthContext';
import { Truck, MapPin, Navigation, ArrowRight, CheckCircle2, Clock, Zap, AlertCircle } from 'lucide-react';

export default function LogisticsDashboard() {
  const { user } = useAuth();
  const [deliveries, setDeliveries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  // AI Route Optimizer State
  const [depot, setDepot] = useState({
    name: 'Karnal Farmer Regional Aggregation Mandi',
    address: 'GT Road Collection Hub, Karnal',
    lat: 29.6857,
    lng: 76.9905,
  });

  const [stops, setStops] = useState([
    { id: 1, name: 'Delhi Azadpur Wholesale Mandi', address: 'Azadpur, New Delhi', lat: 28.7126, lng: 77.1755, order_id: 101 },
    { id: 2, name: 'Gurugram Retail Supermarket Hub', address: 'Sector 29, Gurugram', lat: 28.4682, lng: 77.0635, order_id: 102 },
    { id: 3, name: 'Sonipat Distribution Warehouse', address: 'Sonipat Industrial Area', lat: 28.9931, lng: 77.0151, order_id: 103 },
    { id: 4, name: 'Noida Bulk Institutional Buyer', address: 'Sector 62, Noida', lat: 28.6280, lng: 77.3649, order_id: 104 },
  ]);

  const [newStop, setNewStop] = useState({ name: '', address: '', lat: '', lng: '' });
  const [optimizationResult, setOptimizationResult] = useState(null);
  const [optimizing, setOptimizing] = useState(false);

  const fetchDeliveries = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await api.getDeliveries();
      setDeliveries(data);
    } catch (err) {
      setError(err.message || 'Failed to load deliveries');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDeliveries();
  }, []);

  const handleUpdateStatus = async (deliveryId, status) => {
    try {
      await api.updateDeliveryStatus(deliveryId, status);
      setSuccessMsg(`Delivery #${deliveryId} marked as ${status}`);
      fetchDeliveries();
      setTimeout(() => setSuccessMsg(''), 3000);
    } catch (err) {
      setError(err.message || 'Status update failed');
    }
  };

  const handleRunOptimization = async () => {
    try {
      setOptimizing(true);
      setError('');
      const res = await api.optimizeRoute(depot, stops);
      setOptimizationResult(res);
      setSuccessMsg('AI 2-Opt Route Optimization completed successfully!');
      setTimeout(() => setSuccessMsg(''), 4000);
    } catch (err) {
      setError(err.message || 'Optimization failed');
    } finally {
      setOptimizing(false);
    }
  };

  const handleAddStop = (e) => {
    e.preventDefault();
    if (!newStop.name || !newStop.lat || !newStop.lng) return;
    setStops((prev) => [
      ...prev,
      {
        id: Date.now(),
        name: newStop.name,
        address: newStop.address || newStop.name,
        lat: parseFloat(newStop.lat),
        lng: parseFloat(newStop.lng),
        order_id: Math.floor(Math.random() * 900) + 100,
      },
    ]);
    setNewStop({ name: '', address: '', lat: '', lng: '' });
  };

  const handleRemoveStop = (id) => {
    setStops((prev) => prev.filter((s) => s.id !== id));
  };

  return (
    <div className="page-container">
      <div className="dashboard-header">
        <div>
          <h1>Logistics & Delivery Route Optimization</h1>
          <p className="page-subtitle">
            Coordinate deliveries and run algorithmic Traveling Salesperson Problem (TSP) 2-Opt route sequencing.
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

      {/* AI ROUTE OPTIMIZATION SECTION */}
      <section className="card route-optimizer-card">
        <div className="optimizer-title-bar">
          <div>
            <h2><Zap className="highlight-icon" size={24} /> AI Delivery Route Optimizer</h2>
            <p className="muted-text">
              Solves multi-stop routing using Haversine distance matrix and 2-Opt iterative edge-exchange optimization.
            </p>
          </div>
          <button
            onClick={handleRunOptimization}
            className="btn btn-primary"
            disabled={optimizing || stops.length < 2}
          >
            <Navigation size={18} /> {optimizing ? 'Calculating Shortest Path...' : 'Optimize Multi-Stop Route'}
          </button>
        </div>

        {/* Starting Depot Info */}
        <div className="depot-box">
          <MapPin size={20} className="depot-icon" />
          <div className="depot-info">
            <strong>Starting Collection Depot (Farm Hub):</strong>
            <span>{depot.name} ({depot.address})</span>
            <span className="coord-chip">Coordinates: {depot.lat}, {depot.lng}</span>
          </div>
        </div>

        {/* Current Stops List */}
        <div className="stops-management">
          <h3>Delivery Stops in Batch ({stops.length})</h3>
          <div className="stops-grid">
            {stops.map((stop, idx) => (
              <div key={stop.id} className="stop-card">
                <div className="stop-badge">Stop #{idx + 1}</div>
                <div className="stop-content">
                  <strong>{stop.name}</strong>
                  <span className="stop-addr">{stop.address}</span>
                  <span className="coord-chip">Lat: {stop.lat.toFixed(4)}, Lng: {stop.lng.toFixed(4)}</span>
                </div>
                <button
                  onClick={() => handleRemoveStop(stop.id)}
                  className="btn-remove-stop"
                  title="Remove stop"
                >
                  ×
                </button>
              </div>
            ))}
          </div>

          {/* Add Stop Inline Form */}
          <form onSubmit={handleAddStop} className="add-stop-form">
            <input
              type="text"
              placeholder="Stop Name (e.g. Faridabad Mandi)"
              value={newStop.name}
              onChange={(e) => setNewStop({ ...newStop, name: e.target.value })}
              required
            />
            <input
              type="text"
              placeholder="Address / Sector"
              value={newStop.address}
              onChange={(e) => setNewStop({ ...newStop, address: e.target.value })}
            />
            <input
              type="number"
              step="0.0001"
              placeholder="Latitude (e.g. 28.4089)"
              value={newStop.lat}
              onChange={(e) => setNewStop({ ...newStop, lat: e.target.value })}
              required
            />
            <input
              type="number"
              step="0.0001"
              placeholder="Longitude (e.g. 77.3178)"
              value={newStop.lng}
              onChange={(e) => setNewStop({ ...newStop, lng: e.target.value })}
              required
            />
            <button type="submit" className="btn btn-outline">+ Add Stop</button>
          </form>
        </div>

        {/* Optimization Comparison Results */}
        {optimizationResult && (
          <div className="optimization-results-panel">
            <h3>Optimization Metrics & Savings Comparison</h3>

            <div className="comparison-metrics-grid">
              <div className="metric-box baseline-box">
                <span className="metric-label">Baseline (Sequential) Route</span>
                <span className="metric-value">{optimizationResult.baseline_distance_km} km</span>
                <span className="metric-sub">Est. Time: {optimizationResult.baseline_estimated_time_min} mins</span>
              </div>

              <div className="metric-box optimized-box">
                <span className="metric-label">AI 2-Opt Optimized Route</span>
                <span className="metric-value green-text">{optimizationResult.optimized_distance_km} km</span>
                <span className="metric-sub">Est. Time: {optimizationResult.optimized_estimated_time_min} mins</span>
              </div>

              <div className="metric-box savings-box">
                <span className="metric-label">Total Distance Saved</span>
                <span className="metric-value">{optimizationResult.distance_saved_km} km</span>
                <span className="savings-badge">
                  {optimizationResult.percentage_saved}% Mileage Reduction
                </span>
              </div>

              <div className="metric-box savings-box">
                <span className="metric-label">Delivery Time Saved</span>
                <span className="metric-value">{optimizationResult.time_saved_minutes} mins</span>
                <span className="savings-badge">Quicker Farm-to-Fork Turnaround</span>
              </div>
            </div>

            {/* Turn Sequence */}
            <div className="route-sequence-timeline">
              <h4>Optimized Turn-by-Turn Delivery Sequence</h4>
              <div className="sequence-steps">
                {optimizationResult.optimized_stops.map((step, idx) => (
                  <div key={idx} className="sequence-step-item">
                    <div className="step-number-circle">{step.stop_number}</div>
                    <div className="step-details">
                      <strong>{step.name}</strong>
                      <span className="step-addr">{step.address}</span>
                      {step.leg_distance_km > 0 && (
                        <span className="leg-badge">
                          +{step.leg_distance_km} km from previous stop
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </section>

      {/* DELIVERIES MANAGEMENT SECTION */}
      <section className="card dashboard-table-card">
        <h3>Assigned Deliveries ({deliveries.length})</h3>
        {deliveries.length === 0 ? (
          <p className="empty-hint">No active delivery assignments found. New customer orders will show here for pickup coordination.</p>
        ) : (
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Delivery #</th>
                  <th>Order #</th>
                  <th>Pickup (Farmer Hub)</th>
                  <th>Delivery Destination</th>
                  <th>Est. Distance</th>
                  <th>Current Status</th>
                  <th>Update Action</th>
                </tr>
              </thead>
              <tbody>
                {deliveries.map((del) => (
                  <tr key={del.id}>
                    <td>#{del.id}</td>
                    <td>#{del.order_id}</td>
                    <td>{del.pickup_address || 'Regional Collection Center'}</td>
                    <td>{del.delivery_address}</td>
                    <td>{del.estimated_distance_km ? `${del.estimated_distance_km} km` : '15 km'}</td>
                    <td>
                      <span className={`status-pill status-${del.status}`}>
                        {del.status.replace('_', ' ').toUpperCase()}
                      </span>
                    </td>
                    <td>
                      <div className="status-action-btns">
                        {del.status === 'assigned' && (
                          <button
                            onClick={() => handleUpdateStatus(del.id, 'accepted')}
                            className="btn btn-sm btn-primary"
                          >
                            Accept
                          </button>
                        )}
                        {del.status === 'accepted' && (
                          <button
                            onClick={() => handleUpdateStatus(del.id, 'picked_up')}
                            className="btn btn-sm btn-primary"
                          >
                            Mark Picked Up
                          </button>
                        )}
                        {del.status === 'picked_up' && (
                          <button
                            onClick={() => handleUpdateStatus(del.id, 'in_transit')}
                            className="btn btn-sm btn-primary"
                          >
                            In Transit
                          </button>
                        )}
                        {del.status === 'in_transit' && (
                          <button
                            onClick={() => handleUpdateStatus(del.id, 'delivered')}
                            className="btn btn-sm btn-primary"
                          >
                            Mark Delivered
                          </button>
                        )}
                        {del.status === 'delivered' && (
                          <span className="green-text">✅ Delivered</span>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
