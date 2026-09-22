// src/components/graph/GraphIntelligence.tsx
//
// Graph Intelligence — Canonical F3 (B.3a Integration)
//
// Layout:
//   1. Summary card (entities / relationships / structural hubs)
//   2. GraphVisualization (Cytoscape render, canonical F3)
//   3. GraphEntityExplorer (structural hubs, canonical F3)
//
// Boundary:
//   - GraphNodeDTO FROZEN. No risk_score / confidence / hub list.
//   - Structural ranking is degree-based.
//   - No fabricated "High Risk Hubs" concept.
//
// Props:
//   - caseId: required (drives canonical F3 fetch)
//   - intelligence: optional (for summary card if parent passes)

import React, { useState } from 'react';
import { Network, GitBranch, GitBranchPlus } from 'lucide-react';
import { IntelligenceModel } from '../../services/intelligenceAdapter';
import GraphVisualization from './GraphVisualization';
import GraphEntityExplorer from './GraphEntityExplorer';

interface Props {
  caseId: string;
  intelligence?: IntelligenceModel | null;
}

export default function GraphIntelligence({ caseId, intelligence }: Props) {
  const entities = intelligence?.graph?.entities ?? 0;
  const relationships = intelligence?.graph?.relationships ?? 0;

  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);

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
          <div className="bg-gray-900 rounded-xl p-5">
            <div className="flex gap-2 items-center text-gray-400 text-sm">
              <Network className="w-4 h-4" />
              Entities
            </div>
            <p className="text-3xl font-bold text-white mt-2">
              {entities}
            </p>
          </div>

          <div className="bg-gray-900 rounded-xl p-5">
            <div className="flex gap-2 items-center text-gray-400 text-sm">
              <GitBranch className="w-4 h-4" />
              Relationships
            </div>
            <p className="text-3xl font-bold text-white mt-2">
              {relationships}
            </p>
          </div>

          <div className="bg-gray-900 rounded-xl p-5">
            <div className="flex gap-2 items-center text-gray-400 text-sm">
              <GitBranchPlus className="w-4 h-4" />
              Structural Hubs
            </div>
            <p className="text-3xl font-bold text-cyan-400 mt-2">
              ↓
            </p>
            <p className="text-xs text-gray-500 mt-1">
              Ranked below by degree
            </p>
          </div>
        </div>

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

      {/* VISUALIZATION */}
      <div className="bg-dark-card border border-dark-border rounded-xl overflow-hidden">
        <GraphVisualization
          caseId={caseId}
          onNodeSelect={(node) => {
            setSelectedNodeId(node?.business_key ?? null);
          }}
        />
      </div>

      {/* STRUCTURAL HUBS */}
      <GraphEntityExplorer
        caseId={caseId}
        onNodeSelect={(nodeId) => setSelectedNodeId(nodeId)}
        selectedNodeId={selectedNodeId}
        limit={25}
      />
    </div>
  );
}
