import apiClient from './client';

export const evidenceApi = {
  getStats: () => 
    apiClient.get('/api/v1/evidence/stats'),
  
  getEvidenceById: (id: string) => 
    apiClient.get(`/api/v1/evidence/${id}`),
  
  getCustodyHistory: (id: string) => 
    apiClient.get(`/api/v1/evidence/${id}/custody`),
  
  getEvidenceStats: () => 
    apiClient.get('/api/v1/evidence/stats'),
  
  listEvidence: (caseId?: string) => 
    apiClient.get('/api/v1/evidence', { 
      params: caseId ? { case_id: caseId } : undefined 
    }),
  
  uploadEvidence: (data: any) => 
    apiClient.post('/api/v1/evidence', data),
  
  verifyEvidence: (id: string) => 
    apiClient.post(`/api/v1/evidence/${id}/verify`),
  
  rejectEvidence: (id: string, reason?: string) => 
    apiClient.post(`/api/v1/evidence/${id}/reject`, { reason }),
};

export default evidenceApi;
