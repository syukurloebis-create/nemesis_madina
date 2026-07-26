import { apiClient } from './client';

export const riskApi = {
  getCaseRiskExplanations: async (caseId: string) => {
    if (!caseId) {
      console.warn('[RiskApi] ⚠️ Missing caseId');
      return {};
    }
    const response = await apiClient.get(`/api/v1/cases/${caseId}/risk-explanations`);
    return response;
  },
  
  getTrend: async (days: number = 30) => {
    const response = await apiClient.get('/api/v1/cases/stats');
    return response;
  },
};

export default riskApi;
