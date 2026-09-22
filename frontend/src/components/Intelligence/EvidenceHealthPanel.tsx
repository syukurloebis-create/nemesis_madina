// src/components/Intelligence/EvidenceHealthPanel.tsx
//
// Evidence Health — Canonical (Phase C.3)
//
// Data source: intelligence.evidence (from intelligenceAdapter)
//
// Canonical fields:
//   score, level, total, verified, rejected, pending,
//   avg_trust, avg_confidence, availability, engine, engine_status
//
// availability states:
//   AVAILABLE       — evidence exists, display details
//   NO_DATA         — total = 0, no evidence registered
//   NOT_AVAILABLE   — backend does not expose field
//   ERROR           — fetch/parse failure
//
// Boundary:
//   - No legacy fields (confidence_level, components, custody_events,
//     recommendation) — these are NOT in canonical adapter.
//   - No fabrication.
//   - Empty state = business state, not error.

import React from 'react';
import { ShieldCheck, FileCheck, AlertTriangle } from 'lucide-react';
import type { IntelligenceModel } from '../../services/intelligenceAdapter';

interface Props {
  intelligence: IntelligenceModel;
}

export default function EvidenceHealthPanel({ intelligence }: Props) {
  const evidence = intelligence?.evidence;

  // ─── Empty model fallback ───────────────────────────────────────
  if (!evidence) {
    return null;
  }

  const availability = evidence.availability ?? 'NOT_AVAILABLE';

  // ─── NOT_AVAILABLE state ────────────────────────────────────────
  if (availability === 'NOT_AVAILABLE') {
    return (
      <section className="bg-dark-card border border-dark-border rounded-xl p-6">
        <div className="text-center py-10">
          <ShieldCheck className="mx-auto mb-3 w-12 h-12 text-gray-600" />
          <h2 className="text-lg font-semibold text-white">
            Evidence Health
          </h2>
          <p className="mt-2 text-sm text-gray-400">
            Evidence data is not available from the API.
          </p>
        </div>
      </section>
    );
  }

  // ─── ERROR state ────────────────────────────────────────────────
  if (availability === 'ERROR') {
    return (
      <section className="bg-dark-card border border-dark-border rounded-xl p-6">
        <div className="text-center py-10">
          <AlertTriangle className="mx-auto mb-3 w-12 h-12 text-red-500" />
          <h2 className="text-lg font-semibold text-white">
            Evidence Health
          </h2>
          <p className="mt-2 text-sm text-red-300">
            Failed to load evidence data.
          </p>
        </div>
      </section>
    );
  }

  // ─── NO_DATA state ──────────────────────────────────────────────
  if (availability === 'NO_DATA') {
    return (
      <section className="bg-dark-card border border-dark-border rounded-xl p-6">
        <div className="text-center py-10">
          <FileCheck className="mx-auto mb-3 w-12 h-12 text-gray-600" />
          <h2 className="text-lg font-semibold text-white">
            Evidence Health
          </h2>
          <p className="mt-2 text-sm text-gray-400">
            No evidence has been registered for this case.
          </p>
          <p className="mt-1 text-xs text-gray-500">
            Impact on current risk: {evidence.score.toFixed(2)}
          </p>
          <button
            type="button"
            disabled
            className="mt-6 px-4 py-2 rounded-lg bg-gray-800 text-gray-500 cursor-not-allowed text-sm"
            title="Not yet available in this environment"
          >
            Register Evidence
          </button>
          <p className="mt-2 text-xs text-gray-600">
            Not yet available in this environment.
          </p>
        </div>
      </section>
    );
  }

  // ─── AVAILABLE state (canonical fields only) ────────────────────
  return (
    <section className="bg-dark-card border border-dark-border rounded-xl p-6 space-y-6">
      {/* HEADER */}
      <div className="flex justify-between items-start">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <ShieldCheck className="text-green-400" />
            Evidence Intelligence
          </h2>
          <p className="text-sm text-gray-400">
            Evidence reliability assessment
          </p>
        </div>
        <div className="px-3 py-2 rounded-lg border text-sm text-green-400 bg-green-500/10 border-green-500/30">
          {evidence.level || 'UNKNOWN'}
        </div>
      </div>

      {/* SCORE SUMMARY */}
      <div className="grid grid-cols-4 gap-4">
        <StatCard label="Evidence Score" value={evidence.score.toFixed(2)} tone="text-white" />
        <StatCard label="Total Evidence" value={String(evidence.total)} tone="text-white" />
        <StatCard label="Verified" value={String(evidence.verified)} tone="text-green-400" />
        <StatCard label="Rejected" value={String(evidence.rejected)} tone="text-red-400" />
      </div>

      {/* ADDITIONAL METRICS */}
      <div className="grid grid-cols-3 gap-4">
        <StatCard label="Pending" value={String(evidence.pending)} tone="text-yellow-400" />
        <StatCard label="Avg Trust" value={evidence.avg_trust.toFixed(2)} tone="text-white" />
        <StatCard label="Avg Confidence" value={evidence.avg_confidence.toFixed(2)} tone="text-white" />
      </div>
    </section>
  );
}

function StatCard({
  label,
  value,
  tone,
}: {
  label: string;
  value: string;
  tone: string;
}) {
  return (
    <div className="bg-gray-900 rounded-xl p-4">
      <p className="text-xs text-gray-400">{label}</p>
      <p className={`text-3xl font-bold ${tone}`}>{value}</p>
    </div>
  );
}
