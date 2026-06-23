import { apiClient } from './client';

export const intelligenceApi = {
  // Get graph risk intelligence
  getGraphRisk: (caseId: string) => 
    apiClient.get(`/api/v1/intelligence/graph-risk/${caseId}`),
  
  // Get intelligence score
  getScore: (data: any) => 
    apiClient.post('/api/v1/intelligence/score', data),
  
  // Get health status
  getHealth: () => 
    apiClient.get('/api/v1/intelligence/health'),
};

export default intelligenceApi;
