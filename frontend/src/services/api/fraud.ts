import { apiClient } from './client';

export const fraudApi = {
  getStats: async () => {
    const response = await apiClient.get('/api/v1/fraud/stats');
    return response;
  },
  
  getPatterns: async (caseId: string) => {
    const response = await apiClient.get(`/api/v1/fraud/patterns/${caseId}`);
    return response;
  },
  
  getSignals: async (caseId: string) => {
    const response = await apiClient.get(`/api/v1/fraud/signals/${caseId}`);
    return response;
  },

  getFraudPatterns:(caseId:string)=>
   apiClient.get(
   `/api/v1/fraud/patterns/${caseId}`
  ),
};

export default fraudApi;
