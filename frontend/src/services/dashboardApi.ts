import api from './api';

export const dashboardApi = {

  // ==========================================
  // STRATEGIC INTELLIGENCE (PRIMARY)
  // ==========================================
  getStrategicDashboard: () =>
    api.get('/strategic/dashboard'),


  // ==========================================
  // NETWORK INTELLIGENCE
  // ==========================================
  getKeyActors: () =>
    api.get('/api/v1/network/key-actors'),

  getCommunities: () =>
    api.get('/api/v1/network/communities'),


  // ==========================================
  // LEGACY SUPPORT
  // ==========================================
  getExecutive: () =>
    api.get('/api/v1/dashboard/executive/overview'),

  getStats: () =>
    api.get('/api/v1/investigation/stats'),

  getCases: () =>
    api.get('/api/v1/investigation/cases'),

  getRiskTrend: (days:number = 30) =>
    api.get(`/api/v1/investigation/risk-trend?days=${days}`),

  getEvidenceStats: () =>
    api.get('/api/v1/evidence/stats'),

  getTopEvidence: (limit:number = 10) =>
    api.get(`/api/v1/evidence/top?limit=${limit}`)
      .catch(() => ({data:[]})),


  // ==========================================
  // RECOMMENDATION
  // ==========================================
  getRecommendations: () =>
    api.get('/api/v1/recommendations/'),

  getRecommendationSummary: () =>
    api.get('/api/v1/recommendations/summary'),


  // ==========================================
  // GOVERNANCE
  // ==========================================
  getGovernance: () =>
    api.get('/api/v1/dashboard/apip/governance'),


  // ==========================================
  // PROVENANCE
  // ==========================================
  getProvenance:(caseId:string)=>
    api.get(`/api/v1/provenance/case/${caseId}`)

};


export default dashboardApi;
// Intelligence API
getIntelligenceHealth: () => api.get('/api/v1/intelligence/health'),
getIntelligenceDashboard: () => api.get('/api/v1/intelligence/dashboard'),
getGraphRisk: (caseId: string) => api.get(`/api/v1/intelligence/graph-risk/${caseId}`),
calculateIntelligenceScore: (caseId: string, fraudScore: number = 0, evidenceTrust: number = 0) =>
  api.post(`/api/v1/intelligence/score?case_id=${caseId}&fraud_score=${fraudScore}&evidence_trust=${evidenceTrust}`),
