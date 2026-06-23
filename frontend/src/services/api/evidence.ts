import { apiClient } from './client';

export const evidenceApi = {
  // Get evidence by case
  getEvidenceByCase: (caseId: string) => 
    apiClient.get(`/api/v1/evidence/case/${caseId}`),
  
  // Get evidence stats
  getStats: () => 
    apiClient.get('/api/v1/evidence/stats'),
  
  // Get evidence graph
  getGraph: (caseId: string) => 
    apiClient.get(`/api/v1/evidence/graph/${caseId}`),
  
  // Get evidence metrics
  getMetrics: () => 
    apiClient.get('/api/v1/evidence/metrics'),
  
  // Get evidence quality
  getQuality: () => 
    apiClient.get('/api/v1/evidence/quality'),
  
  // Upload evidence
  upload: (data: FormData) => 
    apiClient.post('/api/v1/evidence/upload', data, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  
  // Verify evidence
  verify: (evidenceId: string) => 
    apiClient.post(`/api/v1/evidence/${evidenceId}/verify`),
  
  // Reject evidence
  reject: (evidenceId: string) => 
    apiClient.post(`/api/v1/evidence/${evidenceId}/reject`),
};

export default evidenceApi;
