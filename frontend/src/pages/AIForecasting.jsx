import React, { useState, useEffect } from 'react';
import { api } from '../api';
import { TrendingUp, BarChart2, Calendar, Lightbulb, AlertCircle, Info, CheckCircle2 } from 'lucide-react';

export default function AIForecasting() {
  const [crops, setCrops] = useState([]);
  const [selectedCrop, setSelectedCrop] = useState('Tomatoes');
  const [forecastMonths, setForecastMonths] = useState(6);
  const [forecastData, setForecastData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Load available crops list
  useEffect(() => {
    const loadCrops = async () => {
      try {
        const cropList = await api.getForecastCrops();
        setCrops(cropList);
        if (cropList.length > 0 && !selectedCrop) {
          setSelectedCrop(cropList[0]);
        }
      } catch (err) {
        console.error('Failed to load crop list', err);
      }
    };
    loadCrops();
  }, []);

  // Fetch forecast data when crop or horizon changes
  useEffect(() => {
    if (!selectedCrop) return;
    const fetchForecast = async () => {
      try {
        setLoading(true);
        setError('');
        const data = await api.getDemandForecast(selectedCrop, forecastMonths);
        setForecastData(data);
      } catch (err) {
        setError(err.message || 'Failed to generate demand forecast');
      } finally {
        setLoading(false);
      }
    };
    fetchForecast();
  }, [selectedCrop, forecastMonths]);

  // Find max demand to normalize chart bar heights
  const maxDemand = forecastData
    ? Math.max(
        ...forecastData.historical_data.map((h) => h.demand_kg),
        ...forecastData.forecast.map((f) => f.predicted_demand_kg)
      )
    : 5000;

  return (
    <div className="page-container">
      <div className="dashboard-header">
        <div>
          <h1>AI Agricultural Demand & Price Forecasting</h1>
          <p className="page-subtitle">
            Helping farmers and FPOs plan sowing, harvest schedules, and direct sales through predictive seasonality modeling.
          </p>
        </div>
      </div>

      {error && (
        <div className="alert-banner alert-error">
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      {/* Control Bar: Crop & Horizon Selection */}
      <div className="card forecast-controls-bar">
        <div className="control-group">
          <label>Select Agricultural Produce:</label>
          <div className="crop-selector-pills">
            {crops.map((c) => (
              <button
                key={c}
                className={`crop-pill ${selectedCrop === c ? 'active' : ''}`}
                onClick={() => setSelectedCrop(c)}
              >
                {c}
              </button>
            ))}
          </div>
        </div>

        <div className="control-group horizon-group">
          <label>Forecast Horizon:</label>
          <select
            value={forecastMonths}
            onChange={(e) => setForecastMonths(Number(e.target.value))}
          >
            <option value={3}>Next 3 Months (Quarterly)</option>
            <option value={6}>Next 6 Months (Half-Yearly)</option>
            <option value={9}>Next 9 Months</option>
            <option value={12}>Next 12 Months (Full Annual Cycle)</option>
          </select>
        </div>
      </div>

      {loading ? (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Training time-series regression model on seasonal crop data for {selectedCrop}...</p>
        </div>
      ) : forecastData ? (
        <>
          {/* Key Metric Highlights */}
          <div className="stats-cards-grid">
            <div className="dashboard-stat-card highlight-card">
              <span className="stat-label">Model Accuracy Rating</span>
              <span className="stat-number green-text">{forecastData.metrics.accuracy_percentage}%</span>
              <span className="stat-sub">Based on backtesting validation holdout</span>
            </div>

            <div className="dashboard-stat-card">
              <span className="stat-label">Mean Absolute Error (MAE)</span>
              <span className="stat-number">{forecastData.metrics.mae_demand_kg} kg</span>
              <span className="stat-sub">RMSE: {forecastData.metrics.rmse_demand_kg} kg</span>
            </div>

            <div className="dashboard-stat-card">
              <span className="stat-label">Algorithm Architecture</span>
              <span className="stat-number text-sm">OLS + Multiplicative Seasonality</span>
              <span className="stat-sub">{forecastData.metrics.sample_records_trained} time points evaluated</span>
            </div>

            <div className="dashboard-stat-card">
              <span className="stat-label">Category Classification</span>
              <span className="stat-number">{forecastData.category}</span>
              <span className="stat-sub">Indian agricultural seasonal cycle</span>
            </div>
          </div>

          {/* Actionable Recommendation Box */}
          <div className="card recommendation-card">
            <div className="recommendation-header">
              <Lightbulb className="recommendation-icon" size={24} />
              <h3>Actionable Farmer Decision Insight</h3>
            </div>
            <p className="recommendation-text">{forecastData.farmer_recommendation}</p>
          </div>

          {/* Visual Bar Chart: Historical vs Forecasted Demand */}
          <div className="card chart-card">
            <div className="chart-header">
              <h3>
                <BarChart2 size={20} /> Demand Trend & Projections (Quintals)
              </h3>
              <div className="chart-legend">
                <span className="legend-item"><span className="legend-color legend-hist"></span> Historical Sales</span>
                <span className="legend-item"><span className="legend-color legend-pred"></span> AI Predicted Demand</span>
              </div>
            </div>

            <div className="visual-bars-container">
              {/* Historical Bars */}
              {forecastData.historical_data.map((item, idx) => {
                const heightPct = Math.round((item.demand_kg / maxDemand) * 100);
                return (
                  <div key={`hist-${idx}`} className="bar-column">
                    <div className="bar-wrapper">
                      <div
                        className="bar bar-historical"
                        style={{ height: `${heightPct}%` }}
                        title={`${item.month_label}: ${item.demand_kg} kg @ ₹${item.price_inr_kg}/kg`}
                      >
                        <span className="bar-tooltip">{Math.round(item.demand_kg / 100)} Q</span>
                      </div>
                    </div>
                    <span className="bar-label">{item.month_label.split(' ')[0]}</span>
                    <span className="bar-sublabel">{item.month_label.split(' ')[1].slice(2)}</span>
                  </div>
                );
              })}

              <div className="chart-divider" title="Present Day Division"></div>

              {/* Forecast Bars */}
              {forecastData.forecast.map((item, idx) => {
                const heightPct = Math.round((item.predicted_demand_kg / maxDemand) * 100);
                return (
                  <div key={`pred-${idx}`} className="bar-column">
                    <div className="bar-wrapper">
                      <div
                        className="bar bar-forecasted"
                        style={{ height: `${heightPct}%` }}
                        title={`Forecast ${item.month_label}: ${item.predicted_demand_kg} kg @ ₹${item.predicted_price_inr_kg}/kg`}
                      >
                        <span className="bar-tooltip">{item.predicted_demand_quintals} Q</span>
                      </div>
                    </div>
                    <span className="bar-label bold-label">{item.month_label.split(' ')[0]}</span>
                    <span className="bar-sublabel">{item.month_label.split(' ')[1].slice(2)}</span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Forecast Projections Table */}
          <div className="card dashboard-table-card">
            <h3>Detailed Future Month Projections</h3>
            <div className="table-responsive">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Future Month</th>
                    <th>Projected Demand (Kg)</th>
                    <th>Projected Demand (Quintals)</th>
                    <th>Est. Farm-Gate Price (₹/kg)</th>
                    <th>Estimated Market Value</th>
                  </tr>
                </thead>
                <tbody>
                  {forecastData.forecast.map((f, idx) => (
                    <tr key={idx}>
                      <td><strong>{f.month_label}</strong></td>
                      <td>{f.predicted_demand_kg.toLocaleString()} kg</td>
                      <td><span className="badge badge-success">{f.predicted_demand_quintals} Q</span></td>
                      <td><strong>₹{f.predicted_price_inr_kg}</strong></td>
                      <td>₹{(f.predicted_demand_kg * f.predicted_price_inr_kg).toLocaleString(undefined, { maximumFractionDigits: 0 })}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Model Limitations Disclaimer */}
          <div className="card disclaimer-card">
            <div className="disclaimer-header">
              <Info size={18} />
              <h4>Model Assumptions & Limitations (Transparent AI)</h4>
            </div>
            <p>{forecastData.limitations}</p>
          </div>
        </>
      ) : null}
    </div>
  );
}
