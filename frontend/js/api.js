/**
 * ============================================================
 * API Client — E-Commerce Recommendation System
 * Handles all communication with the Flask backend.
 * ============================================================
 */

const API_BASE = '';  // Same origin

// ── Storage Helpers ───────────────────────────────────────
const Auth = {
  getToken: () => localStorage.getItem('spark_token'),
  setToken: (t) => localStorage.setItem('spark_token', t),
  getUser:  () => JSON.parse(localStorage.getItem('spark_user') || 'null'),
  setUser:  (u) => localStorage.setItem('spark_user', JSON.stringify(u)),
  clear:    () => { localStorage.removeItem('spark_token'); localStorage.removeItem('spark_user'); },
  isLoggedIn: () => !!localStorage.getItem('spark_token'),
  isAdmin:    () => {
    const u = Auth.getUser();
    return u && u.role === 'admin';
  },
};

// ── Core Fetch Wrapper ────────────────────────────────────
async function apiFetch(endpoint, options = {}) {
  const headers = { 'Content-Type': 'application/json', ...options.headers };
  const token = Auth.getToken();
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const response = await fetch(API_BASE + endpoint, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    Auth.clear();
    // Only redirect if on protected admin page
    if (window.location.pathname.includes('admin') && !window.location.pathname.includes('login')) {
      window.location.href = '/login.html';
    }
    return null;
  }

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.error || `HTTP ${response.status}`);
  }

  return data;
}

// ── Authentication API ────────────────────────────────────
const AuthAPI = {
  async register(name, email, password) {
    return apiFetch('/api/register', {
      method: 'POST',
      body: JSON.stringify({ name, email, password }),
    });
  },
  async login(email, password) {
    return apiFetch('/api/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  },
  async me() {
    return apiFetch('/api/me');
  },
};

// ── Products API ──────────────────────────────────────────
const ProductsAPI = {
  async list({ q = '', category = '', page = 1, limit = 20 } = {}) {
    const params = new URLSearchParams({ q, category, page, limit });
    return apiFetch(`/api/products?${params}`);
  },
  async get(productId) {
    return apiFetch(`/api/products/${productId}`);
  },
  async getCategories() {
    return apiFetch('/api/categories');
  },
  async getPopular(limit = 10) {
    return apiFetch(`/api/popular-products?limit=${limit}`);
  },
};

// ── Interactions API ──────────────────────────────────────
const InteractionsAPI = {
  async record(productId, interactionType, rating = null, query = '') {
    return apiFetch('/api/interactions', {
      method: 'POST',
      body: JSON.stringify({
        product_id: productId,
        interaction_type: interactionType,
        rating,
        query,
      }),
    });
  },
  async myInteractions(limit = 20) {
    return apiFetch(`/api/interactions/me?limit=${limit}`);
  },
};

// ── Recommendations API ───────────────────────────────────
const RecsAPI = {
  async forMe(limit = 10) {
    return apiFetch(`/api/recommendations/me?limit=${limit}`);
  },
  async forUser(userId, limit = 10) {
    return apiFetch(`/api/recommendations/${userId}?limit=${limit}`);
  },
  async forCart(cartIds = [], limit = 4) {
    const ids = Array.isArray(cartIds) ? cartIds.join(',') : cartIds;
    return apiFetch(`/api/recommendations/cart?ids=${encodeURIComponent(ids)}&limit=${limit}`);
  },
  async forWishlist(wishlistIds = [], limit = 4) {
    const ids = Array.isArray(wishlistIds) ? wishlistIds.join(',') : wishlistIds;
    return apiFetch(`/api/recommendations/wishlist?ids=${encodeURIComponent(ids)}&limit=${limit}`);
  },
  async getSimilar(productId, limit = 6) {
    return apiFetch(`/api/recommendations/similar/${productId}?limit=${limit}`);
  },
  async getPopular(limit = 10) {
    return apiFetch(`/api/recommendations/popular?limit=${limit}`);
  },
  async byCategory(category, limit = 10) {
    return apiFetch(`/api/recommendations/category/${encodeURIComponent(category)}?limit=${limit}`);
  },
};

// ── Admin API ─────────────────────────────────────────────
const AdminAPI = {
  async getAnalytics() {
    return apiFetch('/api/analytics');
  },
  async trainModel(options = {}) {
    return apiFetch('/api/train-model', {
      method: 'POST',
      body: JSON.stringify(options),
    });
  },
  async modelStatus() {
    return apiFetch('/api/model-status');
  },
  async getUsers() {
    return apiFetch('/api/admin/users');
  },
  async generateDataset() {
    return apiFetch('/api/admin/generate-dataset', { method: 'POST' });
  },
};

// ── Health Check ──────────────────────────────────────────
const HealthAPI = {
  async check() {
    return apiFetch('/api/health');
  },
};

// ── Cloud API (S3 + EMR) ──────────────────────────────────
const CloudAPI = {
  async status() {
    return apiFetch('/api/cloud/status');
  },
  async uploadDataset(useLarge = false) {
    return apiFetch('/api/cloud/upload-dataset', {
      method: 'POST',
      body: JSON.stringify({ use_large: useLarge }),
    });
  },
  async uploadResults() {
    return apiFetch('/api/cloud/upload-results', { method: 'POST' });
  },
  async listS3Objects(prefix = '') {
    return apiFetch(`/api/cloud/s3/objects?prefix=${encodeURIComponent(prefix)}`);
  },
  async launchEMR(options = {}) {
    return apiFetch('/api/cloud/emr/launch', {
      method: 'POST',
      body: JSON.stringify(options),
    });
  },
  async submitEMRJob(clusterId, useLarge = false) {
    return apiFetch('/api/cloud/emr/submit', {
      method: 'POST',
      body: JSON.stringify({ cluster_id: clusterId, use_large: useLarge }),
    });
  },
  async emrStatus(clusterId) {
    return apiFetch(`/api/cloud/emr/status/${clusterId}`);
  },
  async listEMRClusters() {
    return apiFetch('/api/cloud/emr/clusters');
  },
  async terminateEMR(clusterId) {
    return apiFetch('/api/cloud/emr/terminate', {
      method: 'POST',
      body: JSON.stringify({ cluster_id: clusterId }),
    });
  },
  async cloudSetup(useLarge = false) {
    return apiFetch('/api/cloud/setup', {
      method: 'POST',
      body: JSON.stringify({ use_large: useLarge }),
    });
  },
};

// ── Orders API ────────────────────────────────────────────
const OrdersAPI = {
  async placeOrder(payload) {
    return apiFetch('/api/orders/place', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  },
};

// Export to global scope (vanilla JS, no modules)
window.Auth = Auth;
window.AuthAPI = AuthAPI;
window.ProductsAPI = ProductsAPI;
window.InteractionsAPI = InteractionsAPI;
window.RecsAPI = RecsAPI;
window.OrdersAPI = OrdersAPI;
window.AdminAPI = AdminAPI;
window.HealthAPI = HealthAPI;
window.CloudAPI = CloudAPI;
