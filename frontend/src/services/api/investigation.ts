import { apiClient } from './client';

export const investigationApi = {
  // Get all investigations for a case
  getInvestigations: (caseId: string) =>
    apiClient.get(`/api/v1/investigation/case/${caseId}`),
  
  // Get investigation by ID
  getInvestigation: (id: string) =>
    apiClient.get(`/api/v1/investigation/${id}`),
  
  // Create new investigation
  createInvestigation: (data: any) =>
    apiClient.post('/api/v1/investigation/', data),
  
  // Update status
  updateStatus: (id: string, status: string, progress: number) =>
    apiClient.patch(`/api/v1/investigation/${id}/status`, { status, progress }),
  
  // Escalate
  escalate: (id: string, reason: string, targetLevel: string) =>
    apiClient.post(`/api/v1/investigation/${id}/escalate`, { reason, target_level: targetLevel }),
  
  // Get evidence
  getEvidence: (investigationId: string) =>
    apiClient.get(`/api/v1/investigation/${investigationId}/evidence`),
  
  // Get team
  getTeam: (investigationId: string) =>
    apiClient.get(`/api/v1/investigation/${investigationId}/team`),
  
  // Add note
  addNote: (id: string, content: string) =>
    apiClient.post(`/api/v1/investigation/${id}/notes`, { content }),
  
  // Get notes
  getNotes: (id: string) =>
    apiClient.get(`/api/v1/investigation/${id}/notes`),
  
  // Get statistics
  getStats: (caseId: string) =>
    apiClient.get('/api/v1/investigation/stats', { params: { case_id: caseId } }),
};

export default investigationApi;
