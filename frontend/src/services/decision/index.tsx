import apiClient from '../api/client';

export const decisionService = {
  getDecisions: (caseId: string) => 
    apiClient.get(`/api/v1/decisions?case_id=${caseId}`),
  createDecision: (data: any) => 
    apiClient.post('/api/v1/decisions', data),
  updateDecision: (id: string, data: any) => 
    apiClient.put(`/api/v1/decisions/${id}`, data),
};
