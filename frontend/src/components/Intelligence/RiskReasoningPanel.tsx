// src/components/Intelligence/RiskReasoningPanel.tsx
//
// Risk Reasoning Panel — Canonical + Legacy (Truthful)
//
// Backend: GET /api/v1/risk/explanations/{case_id}
//
// CONTRACT GAP (documented):
//   Backend currently returns legacy fields:
//     - anomaly_score
//     - collusion_score
//     - financial_score
//     - temporal_score
//
//   Canonical Risk Engine v3 fields (findings_risk, graph_risk,
//   fraud_risk, evidence_risk, components, weights) are written
//   to DB via /risk/calculate but NOT YET exposed in /risk/explanations.
//
// PRINCIPLE:
//   Do NOT rename legacy fields to canonical names.
//   - If canonical fields present → display as "Canonical Components"
//   - If only legacy fields present → display as "Legacy Risk Signals"
//   - For unavailable values → display "—" (NOT "0")
//
// Risk Engine v3 is FROZEN. This panel is READ-ONLY.

import React from 'react';
import { useRiskExplanation } from '../../hooks/useRiskQueries';

export default function RiskReasoningPanel({ caseId }: { caseId: string }) {
  const { data, isPending, isError, error, refetch } =
    useRiskExplanation(caseId);

  // ─── ERROR STATE ────────────────────────────────────────────────
  if (isError) {
    return (
      <div className="bg-gray-800/50 rounded-xl border border-gray-700 p-6">
        <h3 className="text-lg font-semibold text-white mb-4">
          📊 Risk Reasoning
        </h3>
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4">
          <p className="text-red-400 font-medium">
            Risk reasoning unavailable
          </p>
          <p className="text-gray-400 text-sm mt-1">{error?.message}</p>
          <button
            onClick={() => refetch()}
            className="mt-3 px-3 py-1 bg-red-500/20 text-red-400 rounded text-sm hover:bg-red-500/30 transition"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  // ─── LOADING STATE ──────────────────────────────────────────────
  if (isPending) {
    return (
      <div className="bg-gray-800/50 rounded-xl border border-gray-700 p-6">
        <h3 className="text-lg font-semibold text-white mb-4">
          📊 Risk Reasoning
        </h3>
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-gray-700 rounded w-1/2" />
          <div className="h-20 bg-gray-700 rounded" />
          <div className="h-20 bg-gray-700 rounded" />
        </div>
      </div>
    );
  }

  // ─── NO_DATA STATE ──────────────────────────────────────────────
  if (!data || data.status === 'NO_DATA' || data.score === null) {
    return (
      <div className="bg-gray-800/50 rounded-xl border border-gray-700 p-6">
        <h3 className="text-lg font-semibold text-white mb-4">
          📊 Risk Reasoning
        </h3>
        <div className="bg-gray-900/50 rounded-lg p-4">
          <p className="text-gray-400">
            No risk assessment available for this case.
          </p>
          <p className="text-gray-500 text-sm mt-1">
            Run risk calculation to compute the canonical risk score.
          </p>
        </div>
      </div>
    );
  }

  // ─── SUCCESS STATE ──────────────────────────────────────────────
  const levelStyle =
    data.risk_level === 'CRITICAL'
      ? 'bg-red-500/20 text-red-400 border-red-500/30'
      : data.risk_level === 'HIGH'
      ? 'bg-orange-500/20 text-orange-400 border-orange-500/30'
      : data.risk_level === 'MEDIUM'
      ? 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30'
      : 'bg-green-500/20 text-green-400 border-green-500/30';

  // ─── CANONICAL COMPONENTS (if available) ────────────────────────
  const canonicalComponents = [
    {
      label: 'Findings',
      value: (data as any).findings_risk ?? null,
      weight: (data as any).weights?.findings ?? null,
    },
    {
      label: 'Graph',
      value: (data as any).graph_risk ?? null,
      weight: (data as any).weights?.graph ?? null,
    },
    {
      label: 'Fraud',
      value: (data as any).fraud_risk ?? null,
      weight: (data as any).weights?.fraud ?? null,
    },
    {
      label: 'Evidence',
      value: (data as any).evidence_risk ?? null,
      weight: (data as any).weights?.evidence ?? null,
    },
  ];

  const hasCanonical = canonicalComponents.some(
    (c) => c.value !== null && c.value !== undefined
  );

  // ─── LEGACY SIGNALS (always available) ──────────────────────────
  const legacySignals = [
    { label: 'Anomaly Score', value: data.anomaly_score ?? null },
    { label: 'Collusion Score', value: data.collusion_score ?? null },
    { label: 'Financial Score', value: data.financial_score ?? null },
    { label: 'Temporal Score', value: data.temporal_score ?? null },
  ];

  const renderValue = (v: number | null | undefined) =>
    v === null || v === undefined ? '—' : v.toFixed(2);

  return (
    <div className="bg-gray-800/50 rounded-xl border border-gray-700 p-6">
      <h3 className="text-lg font-semibold text-white mb-4">
        📊 Risk Reasoning
      </h3>

      {/* ── OVERALL SCORE ── */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <p className="text-sm text-gray-400">Overall Risk Score</p>
          <p className="text-3xl font-bold text-white">
            {data.score !== null ? data.score.toFixed(2) : '—'}
          </p>
        </div>
        <div className="text-right">
          <p className="text-sm text-gray-400">Risk Level</p>
          <span
            className={`inline-block px-3 py-1 rounded text-sm font-medium border ${levelStyle}`}
          >
            {data.risk_level}
          </span>
        </div>
      </div>

      {/* ── CANONICAL COMPONENTS ── */}
      <div className="mb-6">
        <p className="text-sm font-medium text-gray-300 mb-3">
          Canonical Components (Risk Engine v3)
        </p>
        {hasCanonical ? (
          <div className="space-y-3">
            {canonicalComponents.map((c) => (
              <div key={c.label}>
                <div className="flex items-center justify-between text-sm mb-1">
                  <span className="text-gray-300">{c.label}</span>
                  <span className="text-white font-mono">
                    {renderValue(c.value)}
                    {c.weight !== null && c.weight !== undefined && (
                      <span className="text-gray-500 ml-2">
                        × {(c.weight * 100).toFixed(0)}%
                      </span>
                    )}
                  </span>
                </div>
                {c.value !== null && c.value !== undefined && (
                  <div className="w-full h-1.5 bg-gray-700 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full ${
                        c.value > 70
                          ? 'bg-red-500'
                          : c.value > 40
                          ? 'bg-yellow-500'
                          : c.value > 0
                          ? 'bg-green-500'
                          : 'bg-gray-600'
                      }`}
                      style={{
                        width: `${Math.min(Math.max(c.value, 0), 100)}%`,
                      }}
                    />
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-gray-900/40 rounded-lg p-3 text-sm text-gray-400">
            Canonical component values are not yet exposed by the backend
            explanation endpoint. See "Legacy Risk Signals" below.
            <p className="text-xs text-gray-500 mt-1">
              Contract gap documented — Risk Engine v3 write path uses
              canonical fields, but read endpoint still returns legacy
              fields.
            </p>
          </div>
        )}
      </div>

      {/* ── LEGACY SIGNALS ── */}
      <div className="mb-6">
        <p className="text-sm font-medium text-gray-300 mb-3">
          Legacy Risk Signals
        </p>
        <div className="space-y-2">
          {legacySignals.map((s) => (
            <div
              key={s.label}
              className="flex items-center justify-between text-sm"
            >
              <span className="text-gray-400">{s.label}</span>
              <span className="text-gray-300 font-mono">
                {renderValue(s.value)}
              </span>
            </div>
          ))}
        </div>
        <p className="text-xs text-gray-500 mt-2">
          Note: legacy fields (anomaly, collusion, financial) are NOT
          equivalent to canonical findings/graph/fraud components.
        </p>
      </div>

      {/* ── FACTORS ── */}
      {data.factors.length > 0 && (
        <div className="mb-6">
          <p className="text-sm font-medium text-gray-300 mb-2">
            Detected Factors
          </p>
          <ul className="space-y-1.5">
            {data.factors.map((factor, index) => (
              <li
                key={index}
                className="flex items-start gap-2 text-sm text-gray-300"
              >
                <span className="text-orange-400 mt-0.5">•</span>
                <span>{factor}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* ── RECOMMENDATIONS ── */}
      {data.recommendations.length > 0 && (
        <div>
          <p className="text-sm font-medium text-gray-300 mb-2">
            Recommended Actions
          </p>
          <ul className="space-y-1.5">
            {data.recommendations.map((rec, index) => (
              <li
                key={index}
                className="flex items-start gap-2 text-sm text-gray-300"
              >
                <span className="text-blue-400 mt-0.5">→</span>
                <span>{rec}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
