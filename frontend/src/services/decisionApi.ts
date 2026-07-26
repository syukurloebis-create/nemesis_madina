import apiClient from './api/client';

export const decisionApi = {
  getDecisions: (caseId: string) =>
    apiClient.get(`/api/v1/decisions?case_id=${caseId}`),

  getDecision: (id: string) =>
    apiClient.get(`/api/v1/decisions/${id}`),

  getDecisionTrace: (id: string) =>
    apiClient.get(`/api/v1/decisions/${id}/trace`),

  updateDecisionStatus: (id: string, status: string) =>
    apiClient.patch(`/api/v1/decisions/${id}/status`, { status }),

  createDecision: (data: any) =>
    apiClient.post('/api/v1/decisions', data),
};

export default decisionApi;
