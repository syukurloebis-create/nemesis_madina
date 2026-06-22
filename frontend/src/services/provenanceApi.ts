// src/services/provenanceApi.ts
import api from './api';
import type { ProvenanceRecord, ProvenanceGraph } from '../types';

const provenanceApi = {
  getProvenance: (caseId: string) => {
    return api.get<ProvenanceRecord[]>(`/api/v1/provenance/case/${caseId}`);
  },
  getProvenanceGraph: (caseId: string) => {
    return api.get<ProvenanceGraph>(`/api/v1/provenance/case/${caseId}/graph`);
  },
  getEntityLineage: (entityId: string) => {
    return api.get<ProvenanceRecord[]>(`/api/v1/provenance/entity/${entityId}`);
  },
};

export default provenanceApi;
