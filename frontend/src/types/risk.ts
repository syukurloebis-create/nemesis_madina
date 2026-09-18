// frontend/src/types/risk.ts
// Risk Engine v3 — Typed Contracts (FROZEN)
//
// Backend: /api/v1/risk/explanations/{case_id}
// Baseline: 47.58 MEDIUM
// Weights: findings 0.30, graph 0.25, fraud 0.30, evidence 0.15
//
// All inputs are risk-direction (0 = no risk, 100 = max risk).
// NO calculation in frontend. Backend owns formula.

export type RiskLevel =
  | 'LOW'
  | 'MEDIUM'
  | 'HIGH'
  | 'CRITICAL'
  | 'NO_DATA'
  | 'ERROR';

export type RiskExplanationStatus = 'OK' | 'NO_DATA' | 'ERROR';

export interface RiskComponents {
  findings_risk: number;
  graph_risk: number;
  fraud_risk: number;
  evidence_risk: number;
}

export interface RiskWeights {
  findings: number;
  graph: number;
  fraud: number;
  evidence: number;
}

/**
 * Canonical risk explanation from backend.
 *
 * Field notes:
 * - `score` may be `null` when status is NO_DATA (no computation yet).
 * - `risk_level` may be NO_DATA or ERROR (semantic, not just LOW/MEDIUM/HIGH/CRITICAL).
 * - `factors` and `recommendations` are backend-provided (not derived in UI).
 * - No frontend should compute the score from components.
 */
export interface RiskExplanation {
  case_id: string;
  status: RiskExplanationStatus;
  score: number | null;
  risk_level: RiskLevel;

  // Legacy/canonical components (backend-provided)
  anomaly_score?: number;
  collusion_score?: number;
  financial_score?: number;
  temporal_score?: number;
  evidence_risk?: number;

  // Backend-provided context
  factors: string[];
  recommendations: string[];

  // Metadata
  calculated_at: string | null;
  timestamp?: string;
}

/**
 * Risk statistics (aggregate across cases).
 */
export interface RiskStats {
  status: 'OK' | 'NO_DATA' | 'ERROR';
  total: number;
  critical: number;
  high: number;
  medium: number;
  low: number;
  avg_score: number;
  timestamp: string;
  message?: string;
}

/**
 * Result of POST /v1/risk/calculate/{case_id}
 */
export interface RiskCalculateResult {
  status: 'OK' | 'ERROR';
  case_id: string;
  result: {
    score: number;
    level: RiskLevel;
    components: RiskComponents;
    weights: RiskWeights;
    factors: string[];
    recommendations: string[];
  };
}