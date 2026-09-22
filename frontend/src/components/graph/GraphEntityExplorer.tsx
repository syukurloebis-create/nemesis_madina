// src/components/graph/GraphEntityExplorer.tsx
//
// Graph Entity Explorer — Phase A.6 (Deferred Migration)
//
// Phase A.6 status:
//   This component will be migrated to canonical F3 graph service
//   (src/services/api/graph.ts) in Phase B, together with the
//   graph visualization work.
//
// Phase A.6 scope:
//   - Remove legacy `fraud.signals.*` references (not in backend).
//   - Remove legacy `graphIntelligenceApi` import.
//   - Show honest "not yet implemented" state.
//
// Boundary:
//   - GraphNodeDTO is FROZEN.
//   - No fabricated hub entities, no risk_score/risk_level.
//   - No client-side risk ranking.

import React from "react";
import { Search, Network } from "lucide-react";
import { IntelligenceModel } from "../../services/intelligenceAdapter";

interface Props {
  intelligence: IntelligenceModel;
}

export default function GraphEntityExplorer({ intelligence }: Props) {
  const entities = intelligence?.graph?.entities ?? 0;
  const relationships = intelligence?.graph?.relationships ?? 0;

  return (
    <div className="bg-dark-card border border-dark-border rounded-xl p-6 space-y-6">
      {/* HEADER */}
      <div className="flex justify-between items-start">
        <div>
          <div className="flex gap-2 items-center">
            <Network className="text-purple-400 w-5 h-5" />
            <h2 className="text-xl font-bold text-white">
              Entity Relationship Explorer
            </h2>
          </div>
          <p className="text-sm text-gray-400 mt-1">
            Hub entity investigation from Graph Intelligence
          </p>
        </div>
        <div className="text-right">
          <p className="text-xs text-gray-400">Hub Entities</p>
          <p className="text-2xl font-bold text-gray-500">—</p>
        </div>
      </div>

      {/* Search (disabled placeholder) */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
        <input
          type="text"
          disabled
          placeholder="Search vendor / entity... (coming in Phase B)"
          className="w-full pl-10 pr-4 py-2 bg-gray-900 border border-gray-700 rounded-lg text-gray-500 cursor-not-allowed"
        />
      </div>

      {/* Status panel */}
      <div className="bg-gray-900/60 border border-gray-700 rounded-lg p-5">
        <div className="flex items-start gap-3">
          <Network className="w-5 h-5 text-gray-500 mt-0.5 shrink-0" />
          <div className="flex-1">
            <p className="text-gray-300 font-medium">
              Structural hub ranking is not yet available in this view.
            </p>
            <p className="text-sm text-gray-500 mt-2">
              The canonical graph exposes{' '}
              <span className="text-white font-mono">{entities}</span>{' '}
              entities and{' '}
              <span className="text-white font-mono">{relationships}</span>{' '}
              relationships for this case. Structural hub detection
              (degree-based ranking) will be implemented in Phase B
              alongside graph visualization.
            </p>
            <p className="text-xs text-gray-600 mt-3">
              Boundary: GraphNodeDTO is FROZEN. No risk_score,
              confidence, or fabricated hub list will be introduced.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
