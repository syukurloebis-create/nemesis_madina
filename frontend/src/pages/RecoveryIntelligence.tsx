// src/pages/RecoveryIntelligence.tsx
//
// Recovery Intelligence — Phase C.5
//
// Purpose: separate concerns clearly:
//   1. Engine status      → is the recovery engine operational?
//   2. Case recovery state → does this case have recovery actions?
//
// Data source: useIntelligenceDashboard(caseId).data.recovery
// Response shape (backend):
//   {
//     business_state: "READY" | "NO_ACTIONS" | ...,
//     actions: [],
//     engine: "recovery",
//     engine_status: "OK" | "ERROR" | ...
//   }
//
// Boundary:
//   - No fabricated fields.
//   - No semantic mixing of engine health with case business state.
//   - Honest empty states.

import React from 'react';
import { Activity, AlertTriangle } from 'lucide-react';
import { useIntelligenceDashboard } from '../hooks/useIntelligenceDashboard';
import { FROZEN_CASE_ID } from '../config/constants';

interface Props {
  caseId?: string;
}

export default function RecoveryIntelligence({ caseId }: Props) {
  const resolvedCaseId = caseId ?? FROZEN_CASE_ID;
  const { data, loading, error } = useIntelligenceDashboard(resolvedCaseId);

  // ─── LOADING STATE ──────────────────────────────────────────────
  if (loading) {
    return (
      <section className="p-6">
        <h1 className="text-2xl font-bold text-white">
          Recovery Intelligence
        </h1>
        <p className="mt-4 text-sm text-gray-400">
          Loading recovery intelligence...
        </p>
      </section>
    );
  }

  // ─── ERROR STATE ────────────────────────────────────────────────
  if (error) {
    return (
      <section className="p-6">
        <h1 className="text-2xl font-bold text-white">
          Recovery Intelligence
        </h1>
        <div className="mt-4 rounded-lg border border-red-500/30 bg-red-500/10 p-4">
          <div className="flex items-start gap-2">
            <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-red-400" />
            <div>
              <p className="text-sm text-red-300">
                Failed to load recovery intelligence.
              </p>
              <p className="mt-1 text-xs text-red-200">{error}</p>
            </div>
          </div>
        </div>
      </section>
    );
  }

  const recovery = data?.recovery;

  // ─── NO RECOVERY DATA ───────────────────────────────────────────
  if (!recovery) {
    return (
      <section className="p-6">
        <h1 className="text-2xl font-bold text-white">
          Recovery Intelligence
        </h1>
        <p className="mt-4 text-sm text-gray-400">
          No recovery data available for this case.
        </p>
      </section>
    );
  }

  const actions = Array.isArray(recovery.actions) ? recovery.actions : [];
  const actionCount = actions.length;
  const engineStatus = recovery.engine_status ?? 'UNKNOWN';
  const businessState = recovery.business_state ?? 'UNKNOWN';

  const engineStatusTone =
    engineStatus === 'OK'
      ? 'text-green-400 border-green-500/30 bg-green-500/10'
      : engineStatus === 'UNKNOWN'
      ? 'text-gray-400 border-gray-500/30 bg-gray-500/10'
      : 'text-red-400 border-red-500/30 bg-red-500/10';

  return (
    <section className="p-6 space-y-6">
      <h1 className="text-2xl font-bold text-white">
        Recovery Intelligence
      </h1>

      {/* ─── ENGINE STATUS ──────────────────────────────────────── */}
      <div className="bg-dark-card border border-dark-border rounded-xl p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-white">
              Recovery Engine
            </h2>
            <p className="mt-1 text-xs text-gray-500">
              Operational status of the recovery engine.
            </p>
          </div>
          <div
            className={`px-3 py-1.5 rounded-lg border text-sm font-medium ${engineStatusTone}`}
          >
            ● {engineStatus}
          </div>
        </div>

        {recovery.engine && (
          <p className="mt-3 text-xs text-gray-500">
            Engine: <span className="font-mono">{recovery.engine}</span>
          </p>
        )}
      </div>

      {/* ─── CASE RECOVERY STATE ────────────────────────────────── */}
      <div className="bg-dark-card border border-dark-border rounded-xl p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-white">
              Case Recovery State
            </h2>
            <p className="mt-1 text-xs text-gray-500">
              Business recovery state for this specific case.
            </p>
          </div>
          <div className="text-right">
            <p className="text-xs text-gray-500">State</p>
            <p className="text-sm font-semibold text-white">
              {businessState}
            </p>
          </div>
        </div>

        <div className="mt-6">
          {actionCount === 0 ? (
            <div className="text-center py-6">
              <Activity className="mx-auto mb-2 h-8 w-8 text-gray-600" />
              <p className="text-sm text-gray-400">
                No recovery actions defined for this case.
              </p>
              <p className="mt-1 text-xs text-gray-600">
                Actions will appear here once the recovery engine produces them.
              </p>
            </div>
          ) : (
            <div>
              <p className="text-xs text-gray-500 mb-2">
                {actionCount} {actionCount === 1 ? 'action' : 'actions'} defined
              </p>
              <ul className="space-y-2">
                {actions.map((action: any, index: number) => (
                  <li
                    key={action?.id ?? index}
                    className="rounded-lg border border-gray-700 bg-gray-900/40 p-3 text-sm text-gray-300"
                  >
                    {action?.description ?? action?.title ?? String(action)}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
