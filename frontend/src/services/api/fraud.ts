import { apiClient } from './client';

export const fraudApi = {
  // Get fraud patterns
  getPatterns: (caseId: string) => 
    apiClient.get(`/api/v1/fraud/patterns/${caseId}`),
  
  // Get fraud signals
  getSignals: (caseId: string) => 
    apiClient.get(`/api/v1/fraud/signals/${caseId}`),
  
  // Get fraud stats
  getStats: () => 
    apiClient.get('/api/v1/fraud/stats'),
};

export default fraudApi;
