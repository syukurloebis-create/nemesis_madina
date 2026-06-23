import { apiClient } from './client';

export const recommendationApi = {
  // Get recommendations
  getRecommendations: (params?: any) => 
    apiClient.get('/api/v1/recommendations', { params }),
  
  // Get recommendation by ID
  getRecommendation: (id: string) => 
    apiClient.get(`/api/v1/recommendations/${id}`),
  
  // Create recommendation
  create: (data: any) => 
    apiClient.post('/api/v1/recommendations', data),
  
  // Get summary
  getSummary: () => 
    apiClient.get('/api/v1/recommendations/summary'),
  
  // Approve recommendation
  approve: (id: string, data: any) => 
    apiClient.post(`/api/v1/recommendations/${id}/approve`, data),
  
  // Reject recommendation
  reject: (id: string, data: any) => 
    apiClient.post(`/api/v1/recommendations/${id}/reject`, data),
  
  // Implement recommendation
  implement: (id: string) => 
    apiClient.post(`/api/v1/recommendations/${id}/implement`),
};

export default recommendationApi;
