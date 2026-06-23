import { apiClient } from './client';

export const riskApi = {
  // Get risk scores for a case
  getScores: (caseId: string) => 
    apiClient.get('/api/v1/risk/scores', { params: { case_id: caseId } }),
  
  // Get risk explanations for a case
  getExplanations: (caseId: string) => 
    apiClient.get(`/api/v1/risk/explanations/${caseId}`),
  
  // Get case risk explanations (alternative endpoint)
  getCaseRiskExplanations: (caseId: string) => 
    apiClient.get(`/api/v1/cases/${caseId}/risk-explanations`),
  
  // Get historical risk data
  getHistorical: (caseId: string, limit: number = 10) => 
    apiClient.get('/api/v1/risk/historical', { 
      params: { case_id: caseId, limit } 
    }),
  
  // Get risk trend - using cases stats as fallback
  getTrend: (days: number = 30) => 
    apiClient.get('/api/v1/cases/stats').catch(() => ({ data: { trend: [] } })),
};

export default riskApi;
