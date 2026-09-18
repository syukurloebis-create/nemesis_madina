// frontend/src/services/api/risk.ts
// Risk Engine v3 — Canonical API Adapter
//
// Canonical endpoints (Backend: FROZEN):
//   GET  /api/v1/risk/stats
//   GET  /api/v1/risk/explanations/{case_id}
//   POST /api/v1/risk/calculate/{case_id}
//
// Baseline: 47.58 MEDIUM
// Weights: findings 0.30, graph 0.25, fraud 0.30, evidence 0.15
//
// NOTE: This adapter MUST NOT compute risk. Formula is backend-owned.

import { apiClient } from './client';
import type {
  RiskExplanation,
  RiskStats,
  RiskCalculateResult,
} from '@/types/risk';

const BASE = '/v1/risk';

export const riskApi = {
  getStats: (): Promise<RiskStats> =>
    apiClient.get<RiskStats>(`${BASE}/stats`).then(r => r.data),

  getExplanations: (caseId: string): Promise<RiskExplanation> =>
    apiClient
      .get<RiskExplanation>(`${BASE}/explanations/${caseId}`)
      .then(r => r.data),

  calculate: (
    caseId: string,
    fraudScore: number = 0,
  ): Promise<RiskCalculateResult> =>
    apiClient
      .post<RiskCalculateResult>(
        `${BASE}/calculate/${caseId}`,
        null,
        { params: { fraud_score: fraudScore } },
      )
      .then(r => r.data),
};

export default riskApi;