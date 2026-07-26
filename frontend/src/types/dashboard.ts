/**
 * Dashboard Types - Single Source of Truth
 */
export interface DashboardData {
  // Executive Summary
  executive: {
    totalCases: number;
    activeCases: number;
    investigatingCases: number;
    closedCases: number;
    highRiskCases: number;
    criticalAlerts: number;
    avgResolutionTime: number;
    riskScore: number;
    recoveryValue: number;
    exposureValue: number;
  };
  
  // Strategic
  strategic: {
    totalEntities: number;
    totalRelationships: number;
    collusionEdges: number;
    highRiskVendors: number;
    fraudScore: number;
    trustScore: number;
  };
  
  // Intelligence
  intelligence: {
    riskScore: number;
    fraudScore: number;
    graphScore: number;
    evidenceScore: number;
    confidence: number;
    reasoning: string[];
  };
  
  // Graph Risk
  graphRisk: {
    score: number;
    entities: number;
    relationships: number;
    collusion: number;
    centrality: number;
  };
  
  // Actors
  actors: Array<{
    id: string;
    name: string;
    type: string;
    risk: number;
    connections: number;
  }>;
  
  // Cases
  cases: {
    total: number;
    open: number;
    investigating: number;
    closed: number;
    avg_risk_score: number;
  };
  
  // Fraud
  fraud: {
    total: number;
    collusion: number;
    shared_ownership: number;
    financial: number;
    high_confidence: number;
    active_alerts: number;
  };
  
  // Evidence
  evidence: {
    total: number;
    verified: number;
    pending: number;
    rejected: number;
  };
  
  // Procurement
  procurement: {
    total: number;
    high_risk: number;
    medium_risk: number;
    low_risk: number;
    total_value: number;
  };
  
  // System
  systemStatus: {
    status: 'healthy' | 'degraded' | 'down';
    version: string;
    uptime: number;
    services: Record<string, any>;
  };
}

export interface DashboardState {
  data: DashboardData | null;
  loading: boolean;
  error: string | null;
  isStale: boolean;
}