import apiClient from '../api/client';

export interface HealthResponse {
  status: string;
  service: string;
  version: string;
}

export interface CaseStats {
  total: number;
  open: number;
  investigating: number;
  closed: number;
  avg_risk_score: number;
}

export interface FraudStats {
  total: number;
  collusion: number;
  shared_ownership: number;
  financial: number;
  high_confidence: number;
  active_alerts: number;
}

export interface GraphMetrics {
  total_entities: number;
  total_relationships: number;
  collusion_edges: number;
}

export interface RiskStats {
  total_risk: number;
  high_risk: number;
  medium_risk: number;
  low_risk: number;
  timestamp: string;
}

export const intelligenceService = {
  getHealth: async (): Promise<HealthResponse> => {
    return await apiClient.get('/health');
  },

  getCaseStats: async (): Promise<CaseStats> => {
    return await apiClient.get('/api/v1/cases/stats');
  },

  getFraudStats: async (): Promise<FraudStats> => {
    return await apiClient.get('/api/v1/fraud/stats');
  },

  getGraphMetrics: async (): Promise<GraphMetrics> => {
    return await apiClient.get('/api/v1/graph/metrics');
  },

  getRiskStats: async (): Promise<RiskStats> => {
    return await apiClient.get('/api/v1/risk/stats');
  },
};

export default intelligenceService;