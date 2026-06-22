/**
 * Cases API Service
 */

import { apiClient } from './index';

export interface Case {
  id: string;
  title: string;
  description?: string;
  status: 'OPEN' | 'IN_PROGRESS' | 'CLOSED' | 'ARCHIVED';
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  risk_score: number;
  risk_level: string;
  workflow_stage: string;
  created_at: string;
  updated_at?: string;
  assigned_to?: string;
  created_by?: string;
}

export interface CaseStats {
  total: number;
  open: number;
  in_progress: number;
  closed: number;
  archived: number;
}

export interface RiskExplanation {
  id: string;
  case_id: string;
  factor: string;
  score: number;
  weight: number;
  contribution: number;
  description: string;
  evidence_reference?: string;
}

export const casesApi = {
  /**
   * Get all cases
   */
  getAll: async (params?: { status?: string; limit?: number }): Promise<Case[]> => {
    try {
      const response = await apiClient.get('/api/v1/cases', { params });
      return response.data;
    } catch (error) {
      console.warn('[Cases API] Failed to fetch cases:', error);
      return [];
    }
  },

  /**
   * Get case by ID
   */
  getById: async (id: string): Promise<Case | null> => {
    try {
      const response = await apiClient.get(`/api/v1/cases/${id}`);
      return response.data;
    } catch (error) {
      console.warn(`[Cases API] Failed to fetch case ${id}:`, error);
      return null;
    }
  },

  /**
   * Get case statistics
   */
  getStats: async (): Promise<CaseStats> => {
    try {
      const response = await apiClient.get('/api/v1/cases/stats');
      return response.data;
    } catch (error) {
      console.warn('[Cases API] Failed to fetch stats:', error);
      return {
        total: 0,
        open: 0,
        in_progress: 0,
        closed: 0,
        archived: 0,
      };
    }
  },

  /**
   * Get risk explanations for a case
   */
  getRiskExplanations: async (caseId: string): Promise<RiskExplanation[]> => {
    try {
      const response = await apiClient.get(`/api/v1/cases/${caseId}/risk-explanations`);
      return response.data;
    } catch (error) {
      console.warn(`[Cases API] Failed to fetch risk explanations for ${caseId}:`, error);
      return [];
    }
  },
};

export default casesApi;