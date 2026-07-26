import { apiClient } from './client';

export const investigationsApi = {
  getByCase: async (caseId: string) => {
    const response = await apiClient.get(`/api/v1/investigation/case/${caseId}`);
    return response;
  },
  
  getStats: async (caseId: string) => {
    const response = await apiClient.get('/api/v1/investigation/stats', { params: { case_id: caseId } });
    return response;
  },
  
  updateStatus: async (id: string, status: string, progress?: number) => {
    const response = await apiClient.patch(`/api/v1/investigation/${id}/status`, { status, progress });
    return response;
  },
  
  escalate: async (id: string, reason: string, target_level?: string) => {
    const response = await apiClient.post(`/api/v1/investigation/${id}/escalate`, { 
      reason, 
      target_level: target_level || 'HIGH' 
    });
    return response;
  },
  
  addNote: async (id: string, note: string) => {
    const response = await apiClient.post(`/api/v1/investigation/${id}/notes`, { note });
    return response;
  },
};

export default investigationsApi;
