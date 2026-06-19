import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ============================================
// EVIDENCE ENDPOINTS (tanpa /api/v1 prefix)
// ============================================
export const getEvidenceStats = () => api.get('/evidence/stats');
export const getTopEvidence = (limit: number = 10) => 
  api.get(`/evidence/top?limit=${limit}`);
export const getEvidenceByCase = (caseId: string) => 
  api.get(`/evidence/case/${caseId}`);

// ============================================
// DASHBOARD ENDPOINTS (dengan /api/v1 prefix)
// ============================================
export const getExecutiveOverview = () => api.get('/api/v1/dashboard/executive/overview');
export const getGovernanceMetrics = () => api.get('/api/v1/dashboard/apip/governance');
export const getKeyActors = () => api.get('/api/v1/network/key-actors');
export const getRecommendations = () => api.get('/api/v1/recommendations/');
export const getRecommendationSummary = () => api.get('/api/v1/recommendations/summary');
export const getProvenance = (caseId: string) => 
  api.get(`/api/v1/provenance/case/${caseId}`);
export const getInvestigationStats = () => api.get('/api/v1/investigation/stats');
export const getInvestigationCases = () => api.get('/api/v1/investigation/cases');
export const getRiskTrend = (days: number = 30) => 
  api.get(`/api/v1/investigation/risk-trend?days=${days}`);

export default api;
