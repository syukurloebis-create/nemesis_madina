// services/evidenceApi.ts - Evidence Chain API (FIXED)
import api from './api';
import { Evidence, EvidenceChain, EvidenceStats } from '../types/evidence';

export const evidenceApi = {
  // Get evidence by ID
  getEvidence: async (id: string): Promise<Evidence> => {
    const response = await api.get(`/api/v1/evidence/${id}`);
    return response.data;
  },

  // Get evidence chain
  getEvidenceChain: async (id: string): Promise<EvidenceChain> => {
    const response = await api.get(`/api/v1/evidence/${id}/chain`);
    return response.data;
  },

  // Get evidence stats
  getEvidenceStats: async (): Promise<EvidenceStats> => {
    const response = await api.get('/api/v1/evidence/stats');
    return response.data;
  },

  // Get top evidence
  getTopEvidence: async (limit: number = 10): Promise<Evidence[]> => {
    const response = await api.get(`/api/v1/evidence/top?limit=${limit}`);
    return response.data;
  },

  // Get evidence by case
  getEvidenceByCase: async (caseId: string): Promise<Evidence[]> => {
    const response = await api.get(`/api/v1/evidence/case/${caseId}`);
    return response.data;
  },

  // Verify evidence
  verifyEvidence: async (id: string): Promise<Evidence> => {
    const response = await api.post(`/api/v1/evidence/${id}/verify`);
    return response.data;
  },

  // Reject evidence
  rejectEvidence: async (id: string, reason?: string): Promise<Evidence> => {
    const response = await api.post(`/api/v1/evidence/${id}/reject`, { reason });
    return response.data;
  },

  // Get custody history
  getCustodyHistory: async (evidenceId: string): Promise<any[]> => {
    const response = await api.get(`/api/v1/evidence/${evidenceId}/custody`);
    return response.data;
  }
};

export default evidenceApi;
