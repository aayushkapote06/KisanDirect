/**
 * api.js - Centralized API Service
 * Handles all HTTP requests to FastAPI backend with JWT authorization
 */

const API_BASE_URL = 'http://127.0.0.1:8000/api';

export const api = {
  // Helper for requests
  async request(endpoint, options = {}) {
    const token = localStorage.getItem('token');
    const headers = {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    };

    const res = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (res.status === 204) {
      return null;
    }

    const data = await res.json().catch(() => null);

    if (!res.ok) {
      const errorMsg = data?.detail || 'An unexpected error occurred';
      throw new Error(typeof errorMsg === 'string' ? errorMsg : JSON.stringify(errorMsg));
    }

    return data;
  },

  // Auth Endpoints
  async register(userData) {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  },

  async login(credentials) {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
  },

  async getMe() {
    return this.request('/auth/me');
  },

  // Products Endpoints
  async getProducts(params = {}) {
    const query = new URLSearchParams();
    if (params.category) query.append('category', params.category);
    if (params.search) query.append('search', params.search);
    if (params.min_price) query.append('min_price', params.min_price);
    if (params.max_price) query.append('max_price', params.max_price);
    const qs = query.toString() ? `?${query.toString()}` : '';
    return this.request(`/products${qs}`);
  },

  async getFarmerProducts() {
    return this.request('/products/farmer/me');
  },

  async createProduct(productData) {
    return this.request('/products', {
      method: 'POST',
      body: JSON.stringify(productData),
    });
  },

  async updateProduct(id, productData) {
    return this.request(`/products/${id}`, {
      method: 'PUT',
      body: JSON.stringify(productData),
    });
  },

  async deleteProduct(id) {
    return this.request(`/products/${id}`, {
      method: 'DELETE',
    });
  },

  // Orders Endpoints
  async createOrder(orderData) {
    return this.request('/orders', {
      method: 'POST',
      body: JSON.stringify(orderData),
    });
  },

  async getMyOrders() {
    return this.request('/orders/my');
  },

  async getFarmerOrders() {
    return this.request('/orders/farmer/me');
  },

  async updateOrderStatus(orderId, status) {
    return this.request(`/orders/${orderId}/status`, {
      method: 'PUT',
      body: JSON.stringify({ status }),
    });
  },

  // Logistics Endpoints
  async getDeliveries() {
    return this.request('/logistics/deliveries');
  },

  async assignDelivery(deliveryData) {
    return this.request('/logistics/deliveries/assign', {
      method: 'POST',
      body: JSON.stringify(deliveryData),
    });
  },

  async updateDeliveryStatus(deliveryId, status, notes = '') {
    return this.request(`/logistics/deliveries/${deliveryId}/status`, {
      method: 'PUT',
      body: JSON.stringify({ status, notes }),
    });
  },

  async optimizeRoute(depot, stops) {
    return this.request('/logistics/route-optimize', {
      method: 'POST',
      body: JSON.stringify({ depot, stops }),
    });
  },

  // AI Demand Forecasting Endpoints
  async getForecastCrops() {
    return this.request('/forecasts/crops');
  },

  async getDemandForecast(crop, months = 6) {
    return this.request(`/forecasts/demand?crop=${encodeURIComponent(crop)}&months=${months}`);
  },

  // Admin Endpoints
  async getAdminStats() {
    return this.request('/admin/stats');
  },

  async getAdminUsers() {
    return this.request('/admin/users');
  },

  async toggleUserActive(userId) {
    return this.request(`/admin/users/${userId}/toggle`, {
      method: 'PUT',
    });
  },

  async getAdminOrders() {
    return this.request('/admin/orders');
  },

  // Mandi Market Rates Endpoints
  async getMandiStates() {
    return this.request('/mandi/states');
  },

  async getMandiCommodities() {
    return this.request('/mandi/commodities');
  },

  async getMandiRates(params = {}) {
    const query = new URLSearchParams();
    if (params.state && params.state !== 'All') query.append('state', params.state);
    if (params.commodity && params.commodity !== 'All') query.append('commodity', params.commodity);
    const qs = query.toString() ? `?${query.toString()}` : '';
    return this.request(`/mandi/rates${qs}`);
  },
};
