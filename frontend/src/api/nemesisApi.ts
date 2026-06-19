import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: `${API_BASE}/api/v1`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor untuk token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ============================================================
// API FUNCTIONS
// ============================================================

// Dashboard
export const getDashboardData = () => api.get('/dashboard');

// Executive
export const getExecutiveOverview = () => api.get('/dashboard/executive/overview');
export const getExecutiveRiskMap = () => api.get('/dashboard/executive/risk-map');
export const getExecutiveTrend = () => api.get('/dashboard/executive/trend');

// Evidence
export const getEvidenceStats = () => api.get('/evidence/stats');
export const getEvidenceScore = (id: string) => api.get(`/evidence/${id}/score`);

// Provenance
export const getCaseProvenance = (id: string) => api.get(`/provenance/case/${id}`);

// Network
export const getKeyActors = () => api.get('/network/key-actors');
export const getCommunities = () => api.get('/network/communities');

// Governance
export const getGovernanceMetrics = () => api.get('/dashboard/apip/governance');

// Recommendations
export const getRecommendations = () => api.get('/recommendations');

// Cases
export const getCases = () => api.get('/cases/');

export default api;
