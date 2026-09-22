// src/components/graph/GraphIntelligence.tsx
//
// Graph Intelligence — Canonical F3 (Read-only Summary)
//
// Sources:
//   intelligence.graph.entities        (from /dashboard/intelligence)
//   intelligence.graph.relationships   (from /dashboard/intelligence)
//
// Boundary:
//   - GraphNodeDTO is FROZEN. Do NOT add risk_score / risk_level / hub list.
//   - Structural hubs are computed from canonical F3 API
//     (see GraphEntityExplorer / Phase B visualization).
//   - No fabricated "High Risk Hubs" concept.

import React from "react";
import { Network, GitBranch, GitBranchPlus } from "lucide-react";
import { IntelligenceModel } from "../../services/intelligenceAdapter";
import GraphEntityExplorer from "./GraphEntityExplorer";

interface Props {
  intelligence: IntelligenceModel;
}

export default function GraphIntelligence({ intelligence }: Props) {
  const entities = intelligence?.graph?.entities ?? 0;
  const relationships = intelligence?.graph?.relationships ?? 0;

  const hubsAvailability =
    intelligence?.graph?.structuralHubs?.availability ?? 'NOT_AVAILABLE';

  return (
    <div className="space-y-6">
      {/* GRAPH SUMMARY */}
      <div className="bg-dark-card border border-dark-border rounded-xl p-6">
        <div className="flex items-center gap-3 mb-6">
          <Network className="text-purple-400 w-6 h-6" />
          <div>
            <h2 className="text-xl font-bold text-white">
              Graph Intelligence
            </h2>
            <p className="text-sm text-gray-400">
              Entity relationship analysis
            </p>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4">
          {/* Entities */}
          <div className="bg-gray-900 rounded-xl p-5">
            <div className="flex gap-2 items-center text-gray-400 text-sm">
              <Network className="w-4 h-4" />
              Entities
            </div>
            <p className="text-3xl font-bold text-white mt-2">
              {entities}
            </p>
          </div>

          {/* Relationships */}
          <div className="bg-gray-900 rounded-xl p-5">
            <div className="flex gap-2 items-center text-gray-400 text-sm">
              <GitBranch className="w-4 h-4" />
              Relationships
            </div>
            <p className="text-3xl font-bold text-white mt-2">
              {relationships}
            </p>
          </div>

          {/* Structural Hubs (honest state) */}
          <div className="bg-gray-900 rounded-xl p-5">
            <div className="flex gap-2 items-center text-gray-400 text-sm">
              <GitBranchPlus className="w-4 h-4" />
              Structural Hubs
            </div>
            <p className="text-3xl font-bold text-gray-400 mt-2">
              —
            </p>
            <p className="text-xs text-gray-500 mt-1">
              {hubsAvailability === 'NOT_AVAILABLE'
                ? 'See Entity Explorer below'
                : 'Available'}
            </p>
          </div>
        </div>

        {/* Honest note about structural ranking */}
        <div className="mt-6 bg-gray-900/40 border border-gray-700 rounded-lg p-3">
          <p className="text-xs text-gray-400">
            <span className="text-gray-300 font-medium">
              Structural ranking is degree-based.
            </span>{' '}
            Entity ranking reflects relationship counts (structural
            centrality), not risk scores. GraphNodeDTO is FROZEN and does
            not expose risk_score / confidence / id.
          </p>
        </div>
      </div>

      {/* ENTITY DRILL DOWN */}
      <GraphEntityExplorer intelligence={intelligence} />
    </div>
  );
}
