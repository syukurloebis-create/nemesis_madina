// services/provenanceApi.ts - Provenance API calls
import api from './api';
import { ProvenanceData } from '../types/provenance';

export const provenanceApi = {
  getProvenance: async (caseId: string): Promise<ProvenanceData> => {
    const response = await api.get(`/api/v1/provenance/case/${caseId}`);
    return response.data;
  },
  
  getRiskContributors: async (caseId: string) => {
    const data = await provenanceApi.getProvenance(caseId);
    return data.risk_contributors || [];
  },
  
  getDecisionChain: async (caseId: string) => {
    const data = await provenanceApi.getProvenance(caseId);
    return data.decision_chain || [];
  },
  
  generateReport: async (caseId: string) => {
    const response = await api.post(`/api/v1/provenance/case/${caseId}/report`);
    return response.data;
  }
};

export default provenanceApi;
