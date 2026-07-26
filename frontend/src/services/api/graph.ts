import apiClient from './client';

export const graphApi = {
  getMetrics: (caseId?: string) =>
    apiClient.get('/api/v1/graph/metrics', {
      params: caseId ? { case_id: caseId } : undefined
    }),
  
  getKeyActors: (params?: any) =>
    apiClient.get('/api/v1/graph/key-actors', { params }),
  
  getEntities: (caseId?: string) =>
    apiClient.get('/api/v1/graph/entities', {
      params: caseId ? { case_id: caseId } : undefined
    }),
  
  getCommunities: (caseId: string) =>
    apiClient.get(`/api/v1/graph/communities/${caseId}`),
  
  getStats: () =>
    apiClient.get('/api/v1/graph/stats'),
  
  getRelationships: (caseId: string) =>
    apiClient.get(`/api/v1/graph/relationships/${caseId}`),
  
  getEntityGraph: (caseId: string) =>
    apiClient.get(`/api/v1/graph/entities/${caseId}`),
  
  getCollusionCycles: (caseId: string) =>
    apiClient.get(`/api/v1/graph/collusion-cycles/${caseId}`),
};

export default graphApi;
