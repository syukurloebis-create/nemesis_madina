import { api } from './api';

export const dashboardApi = {
  // Executive Dashboard
  getExecutive: () => api.get('/api/v1/dashboard/executive/overview'),
  getStrategicDashboard: () => api.get('/api/v1/dashboard/strategic'),
  
  // Statistics
  getStats: () => api.get('/api/v1/investigation/stats'),
  getCases: () => api.get('/api/v1/investigation/cases'),
  getEvidenceStats: () => api.get('/api/v1/evidence/stats'),
  
  // Risk
  getRiskTrend: (days: number = 30) => 
    api.get(`/api/v1/investigation/risk-trend?days=${days}`),
  
  // Graph
  getKeyActors: () => api.get('/api/v1/graph/key-actors'),
  getEntities: () => api.get('/api/v1/graph/entities'),
  
  // Recommendations
  getRecommendations: () => api.get('/api/v1/recommendations/'),
  getRecommendationSummary: () => api.get('/api/v1/recommendations/summary'),
  
  // Governance
  getGovernance: () => api.get('/api/v1/dashboard/api/governance'),
  
  // Provenance
  getProvenance: (caseId: string) => 
    api.get(`/api/v1/provenance/case/${caseId}`),
};

export default dashboardApi;
