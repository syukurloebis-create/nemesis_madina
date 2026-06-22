/**
 * Evidence API Service
 */

import { apiClient } from './index';

export interface Evidence {
  id: string;
  case_id: string;
  filename: string;
  file_type?: string;
  file_size?: number;
  file_hash?: string;
  status: 'pending' | 'verified' | 'rejected';
  verified_at?: string;
  uploaded_at: string;
  updated_at: string;
}

export interface EvidenceStats {
  total: number;
  pending: number;
  verified: number;
  rejected: number;
  trust_score?: number;
}

export const evidenceApi = {
  /**
   * Get evidence for a case
   */
  getByCase: async (caseId: string): Promise<Evidence[]> => {
    try {
      const response = await apiClient.get(`/api/v1/evidence/by-case/${caseId}`);
      return response.data;
    } catch (error) {
      console.warn(`[Evidence API] Failed to fetch evidence for ${caseId}:`, error);
      return [];
    }
  },

  /**
   * Get evidence statistics
   */
  getStats: async (): Promise<EvidenceStats> => {
    try {
      const response = await apiClient.get('/api/v1/evidence/stats');
      return response.data;
    } catch (error) {
      console.warn('[Evidence API] Failed to fetch stats:', error);
      return {
        total: 0,
        pending: 0,
        verified: 0,
        rejected: 0,
        trust_score: 0,
      };
    }
  },
};

export default evidenceApi;