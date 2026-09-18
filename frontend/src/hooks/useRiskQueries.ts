// src/hooks/useRiskQueries.ts
//
// Risk Engine v3 — React Query hooks.
//
// Backend: GET /api/v1/risk/explanations/{case_id}
//
// CONTRACT NOTE:
//   Backend currently returns legacy fields (anomaly_score, collusion_score,
//   financial_score, temporal_score). Canonical fields (findings_risk,
//   graph_risk, fraud_risk, evidence_risk, components, weights) are written
//   by /risk/calculate but NOT YET exposed in /risk/explanations.
//
//   This is a documented contract gap — see FE-3 commit message.
//
// PRINCIPLE: No frontend risk calculation. Display only.

import { useQuery } from '@tanstack/react-query';
import { riskApi } from '@/services/api/risk';
import type { RiskExplanation } from '@/types/risk';

export function useRiskExplanation(caseId: string | undefined) {
  return useQuery<RiskExplanation>({
    queryKey: ['risk', 'explanation', caseId],
    queryFn: () => riskApi.getExplanations(caseId!),
    enabled: !!caseId,
    staleTime: 60_000,
  });
}
