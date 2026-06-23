import { apiClient } from './client';

export const graphApi = {
  // Get key actors
  getKeyActors: (params?: any) => 
    apiClient.get('/api/v1/graph/key-actors', { params }),
  
  // Get communities
  getCommunities: (caseId: string) => 
    apiClient.get('/api/v1/graph/communities', { params: { case_id: caseId } }),
  
  // Get clusters
  getClusters: (caseId: string) => 
    apiClient.get(`/api/v1/graph/clusters/${caseId}`),
  
  // Get collusion
  getCollusion: (caseId?: string) => 
    apiClient.get('/api/v1/graph/collusion', { params: { case_id: caseId } }),
  
  // Get graph data
  getGraph: (caseId: string) => 
    apiClient.get('/api/v1/graph/graph/', { params: { case_id: caseId } }),
  
  // Get graph metrics
  getMetrics: () => 
    apiClient.get('/api/v1/graph/metrics'),
  
  // Get entities
  getEntities: () => 
    apiClient.get('/api/v1/graph/entities'),
  
  // Get relationships
  getRelationships: () => 
    apiClient.get('/api/v1/graph/relationships'),
  
  // Get vendor network
  getVendorNetwork: (vendorName: string) => 
    apiClient.get(`/api/v1/graph/vendor/${vendorName}/network`),
};

export default graphApi;
