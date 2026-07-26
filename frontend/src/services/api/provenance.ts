import apiClient from './client';

export const provenanceApi = {
  getProvenance: (id: string) =>
    apiClient.get(`/api/v1/provenance/${id}`),
  
  getLineage: (id: string) =>
    apiClient.get(`/api/v1/provenance/${id}/lineage`),
  
  getTrustLineage: (entityId: string) =>
    apiClient.get(`/api/v1/trust/lineage/${entityId}`),
};

export default provenanceApi;
