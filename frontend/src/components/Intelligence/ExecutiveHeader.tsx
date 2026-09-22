// frontend/src/components/Intelligence/ExecutiveHeader.tsx
//
// Executive Header — Canonical Risk Breakdown
//
// Data sources (typed adapters):
//   - riskApi.getExplanations(caseId)  →  RiskExplanation
//
// Backend response for /v1/risk/explanations/{case_id}:
//   {
//     case_id,
//     status: "OK" | "NO_DATA" | "ERROR",
//     score: number | null,
//     risk_level: RiskLevel,
//     anomaly_score?,      // legacy alias → findings_risk
//     collusion_score?,    // legacy alias → graph_risk
//     financial_score?,    // legacy alias → fraud_risk
//     temporal_score?,     // legacy
//     factors: string[],
//     recommendations: string[],
//     calculated_at: string | null,
//   }
//
// NOTE: Backend returns legacy field names. Frontend maps them to
// canonical component names (findings/graph/fraud/evidence).
// This is a known contract gap — will be resolved in a separate
// backend sprint. NOT part of F3 freeze.
//
// PRINCIPLE:
//   "No metric without meaning. No risk without reasoning."
//   "No fallback fabrication."

import React from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  ShieldCheck,
  AlertTriangle,
  Activity,
  TrendingUp,
} from 'lucide-react';

import type { IntelligenceModel } from '../../services/intelligenceAdapter';
import { riskApi } from '../../services/api/risk';
import type { RiskExplanation } from '../../types/risk';
import type { Freshness } from '../../types/semantic';
import { displayFreshness } from '../../types/semantic';
import { formatTimestamp, freshnessStyle } from '../../utils/format';

interface Props {
  intelligence: IntelligenceModel;
}

interface CanonicalComponents {
  findings_risk: number;
  graph_risk: number;
  fraud_risk: number;
  evidence_risk: number;
}

const WEIGHTS = {
  findings: 0.30,
  graph: 0.25,
  fraud: 0.30,
  evidence: 0.15,
} as const;


/**
 * Map backend legacy fields → canonical component names.
 *
 * Backend /v1/risk/explanations/{case_id} currently returns:
 *   - anomaly_score   (canonical: findings_risk)
 *   - collusion_score (canonical: graph_risk)
 *   - financial_score (canonical: fraud_risk)
 *   - evidence_risk   (already canonical)
 */
function extractComponents(data: RiskExplanation | undefined): CanonicalComponents {
  if (!data) {
    return {
      findings_risk: 0,
      graph_risk: 0,
      fraud_risk: 0,
      evidence_risk: 0,
    };
  }
  return {
    findings_risk: data.anomaly_score ?? 0,
    graph_risk: data.collusion_score ?? 0,
    fraud_risk: data.financial_score ?? 0,
    evidence_risk: data.evidence_risk ?? 0,
  };
}

export default function ExecutiveHeader({ intelligence }: Props) {
  const caseId = intelligence?.case_id;

  // ─── Phase C.1: Metadata ────────────────────────────────────────
  const generatedAt = intelligence?.generatedAt ?? null;
  const freshness: Freshness = intelligence?.freshness ?? 'UNKNOWN';
  const requestId = intelligence?.requestId ?? null;

  // ─── Typed query via React Query ────────────────────────────────
  const {
    data: explanation,
    isLoading,
    isError,
  } = useQuery<RiskExplanation>({
    queryKey: ['risk-explanations', caseId],
    queryFn: () => riskApi.getExplanations(caseId as string),
    enabled: !!caseId,
  });

  const components = extractComponents(explanation);
  const componentsLoaded = !!explanation && !isLoading && !isError;

  // ─── Headline data (from intelligence prop) ─────────────────────
  const risk = intelligence?.risk?.level ?? 'UNKNOWN';
  const score = intelligence?.risk?.score ?? 0;
  const fraud = intelligence?.fraud?.overall_risk ?? 'NORMAL';

  // ─── Semantic helpers ───────────────────────────────────────────
  const levelStyle = (level: string) => {
    switch (level) {
      case 'CRITICAL':
        return 'text-red-400 border-red-500/30 bg-red-500/10';
      case 'HIGH':
        return 'text-orange-400 border-orange-500/30 bg-orange-500/10';
      case 'MEDIUM':
        return 'text-yellow-400 border-yellow-500/30 bg-yellow-500/10';
      case 'LOW':
        return 'text-green-400 border-green-500/30 bg-green-500/10';
      default:
        return 'text-gray-400 border-gray-500/30 bg-gray-500/10';
    }
  };

  // ─── Render ─────────────────────────────────────────────────────
  return (
    <div className="bg-dark-card border border-dark-border rounded-xl p-6">
      {/* ─── Header Row ─────────────────────────────────────────── */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <ShieldCheck className="w-6 h-6 text-blue-400" />
          <div>
            <h1 className="text-2xl font-semibold text-white">
              Intelligence Overview
            </h1>
            <p className="text-sm text-gray-400">
              Case: {caseId ?? '—'}
            </p>
            <div className="flex items-center gap-2 mt-1 text-xs text-gray-500">
              <span>
                Last calculated: {formatTimestamp(generatedAt)}
              </span>
              <span className="text-gray-600">·</span>
              <span
                className={`px-1.5 py-0.5 rounded border text-[10px] uppercase tracking-wide ${freshnessStyle(freshness)}`}
              >
                {displayFreshness(freshness)}
              </span>
              {requestId && (
                <>
                  <span className="text-gray-600">·</span>
                  <span className="font-mono" title={requestId}>
                    req: {requestId.slice(0, 8)}
                  </span>
                </>
              )}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-4">
          {/* Overall Risk */}
          <div className={`px-4 py-2 border rounded-lg ${levelStyle(risk)}`}>
            <div className="text-xs uppercase tracking-wide opacity-80">
              Overall Case Risk
            </div>
            <div className="text-2xl font-bold">
              {score} <span className="text-sm font-medium">{risk}</span>
            </div>
          </div>

          {/* Fraud Component */}
          <div className="px-4 py-2 border border-orange-500/30 bg-orange-500/10 rounded-lg">
            <div className="text-xs uppercase tracking-wide text-orange-300">
              Fraud Component
            </div>
            <div className="text-2xl font-bold text-orange-400">
              {fraud}
            </div>
          </div>
        </div>
      </div>

      {/* ─── Canonical Components ───────────────────────────────── */}
      <div className="grid grid-cols-4 gap-4">
        <ComponentCard
          label="Findings"
          value={components.findings_risk}
          weight={WEIGHTS.findings}
          loaded={componentsLoaded}
          error={isError}
        />
        <ComponentCard
          label="Graph"
          value={components.graph_risk}
          weight={WEIGHTS.graph}
          loaded={componentsLoaded}
          error={isError}
        />
        <ComponentCard
          label="Fraud"
          value={components.fraud_risk}
          weight={WEIGHTS.fraud}
          loaded={componentsLoaded}
          error={isError}
        />
        <ComponentCard
          label="Evidence"
          value={components.evidence_risk}
          weight={WEIGHTS.evidence}
          loaded={componentsLoaded}
          error={isError}
        />
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────
// Sub-components
// ─────────────────────────────────────────────────────────────────

interface ComponentCardProps {
  label: string;
  value: number;
  weight: number;
  loaded: boolean;
  error: boolean;
}

function ComponentCard({ label, value, weight, loaded, error }: ComponentCardProps) {
  // ── State semantics ──
  // error  → show "ERROR"
  // !loaded → show "—" (no data yet)
  // loaded  → show value
  let displayValue: string;
  let toneClass: string;

  if (error) {
    displayValue = 'ERROR';
    toneClass = 'text-red-400';
  } else if (!loaded) {
    displayValue = '—';
    toneClass = 'text-gray-500';
  } else {
    displayValue = value.toFixed(2);
    toneClass =
      value >= 70 ? 'text-red-400' :
      value >= 40 ? 'text-yellow-400' :
                    'text-green-400';
  }

  const contribution = loaded && !error ? (value * weight).toFixed(2) : '—';

  return (
    <div className="bg-dark-bg border border-dark-border rounded-lg p-4">
      <div className="flex items-center justify-between mb-1">
        <div className="text-xs uppercase tracking-wide text-gray-400">
          {label}
        </div>
        <div className="text-xs text-gray-500">
          × {(weight * 100).toFixed(0)}%
        </div>
      </div>
      <div className={`text-2xl font-semibold ${toneClass}`}>
        {displayValue}
      </div>
      <div className="text-xs text-gray-500 mt-1">
        Contribution: <span className="text-gray-300">{contribution}</span>
      </div>
    </div>
  );
}