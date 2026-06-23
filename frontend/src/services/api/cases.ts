import { apiClient } from './client';

export const casesApi = {
  // Get all cases
  getCases: (params?: any) => 
    apiClient.get('/api/v1/cases', { params }),
  
  // Get case by ID
  getCase: (caseId: string) => 
    apiClient.get(`/api/v1/cases/${caseId}`),
  
  // Get case stats
  getStats: () => 
    apiClient.get('/api/v1/cases/stats'),
  
  // Get risk explanations for a case
  getRiskExplanations: (caseId: string) => 
    apiClient.get(`/api/v1/cases/${caseId}/risk-explanations`),
  
  // Create case
  createCase: (data: any) => 
    apiClient.post('/api/v1/cases', data),
  
  // Update case
  updateCase: (caseId: string, data: any) => 
    apiClient.put(`/api/v1/cases/${caseId}`, data),
  
  // Delete case
  deleteCase: (caseId: string) => 
    apiClient.delete(`/api/v1/cases/${caseId}`),
};

export default casesApi;
