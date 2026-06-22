/**
 * Risk API Service
 */

import { apiClient } from './index';

export interface RiskScore {
  case_id: string;
  overall_score: number;
  risk_level: string;
  anomaly_score?: number;
  collusion_score?: number;
  financial_score?: number;
  temporal_score?: number;
  factors: Record<string, any>;
  recommendations: string[];
  calculated_at: string;
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

export const riskApi = {
  /**
   * Get risk score for a case
   */
  getScore: async (caseId: string): Promise<RiskScore> => {
    const response = await apiClient.get(`/api/v1/risk/score/${caseId}`);
    return response.data;
  },

  /**
   * Get risk explanations for a case
   */
  getExplanations: async (caseId: string): Promise<RiskExplanation[]> => {
    const response = await apiClient.get(`/api/v1/risk/explanations/${caseId}`);
    return response.data;
  },

  /**
   * Calculate risk for a case
   */
  calculate: async (caseId: string): Promise<RiskScore> => {
    const response = await apiClient.post(`/api/v1/risk/calculate/${caseId}`);
    return response.data;
  },
};

export default riskApi;