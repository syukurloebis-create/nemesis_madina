import apiClient from "./api/client";

export const provenanceApi = {

  getLineage: (id:string) =>
    apiClient.get(`/api/v1/provenance/${id}`),

  getHistory: (id:string) =>
    apiClient.get(`/api/v1/provenance/${id}/history`),

  getGraph: (id:string) =>
    apiClient.get(`/api/v1/provenance/${id}/graph`),

};


export default provenanceApi;