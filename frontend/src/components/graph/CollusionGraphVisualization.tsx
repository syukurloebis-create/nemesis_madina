// src/components/graph/CollusionGraphVisualization.tsx
//
// Collusion Graph Visualization — Canonical F3
//
// Sources (canonical only):
//   graphApi.getCollusion(caseId)  → COLLUSION relationships
//   graphApi.getCaseGraph(caseId)  → node lookup by business_key
//
// Boundary:
//   - GraphNodeDTO is FROZEN. No risk_score / confidence / risk_level.
//   - No fabricated fields. shared_packages shown ONLY if present in
//     canonical extra_data payload.
//   - No legacy api.getEntities().
//   - No demo / fallback nodes.
//
// Layout: circle (deterministic for small subgraph).

import React, { useEffect, useMemo, useState } from 'react';
import CytoscapeComponent from 'react-cytoscapejs';
import cytoscape from 'cytoscape';
import {
  graphApi,
  GraphEdgeDTO,
  GraphNodeDTO,
} from '../../services/api/graph';

interface Props {
  caseId: string;
  onNodeSelect?: (nodeId: string) => void;
  selectedNodeId?: string | null;
}

interface GraphState {
  nodes: GraphNodeDTO[];
  edges: GraphEdgeDTO[];
  loading: boolean;
  error: string | null;
  hasCollusion: boolean;
}

const EMPTY_STATE: GraphState = {
  nodes: [],
  edges: [],
  loading: true,
  error: null,
  hasCollusion: false,
};

function readSharedPackages(edge: GraphEdgeDTO): number | null {
  const raw = (edge.extra_data as Record<string, unknown> | undefined)
    ?.shared_packages;
  return typeof raw === 'number' ? raw : null;
}

function readEntityColor(entityType: string): string {
  switch (entityType) {
    case 'vendor':
      return '#1e3a2f';
    case 'procurement_record':
      return '#1e293b';
    case 'institution':
      return '#3d2a1e';
    default:
      return '#374151';
  }
}

function readEntityBorder(entityType: string): string {
  switch (entityType) {
    case 'vendor':
      return '#10b981';
    case 'procurement_record':
      return '#3b82f6';
    case 'institution':
      return '#f59e0b';
    default:
      return '#6b7280';
  }
}

export const CollusionGraphVisualization: React.FC<Props> = ({
  caseId,
  onNodeSelect,
  selectedNodeId,
}) => {
  const [state, setState] = useState<GraphState>(EMPTY_STATE);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      if (!caseId) {
        setState({
          ...EMPTY_STATE,
          loading: false,
          error: 'Case ID tidak tersedia.',
        });
        return;
      }

      setState({ ...EMPTY_STATE, loading: true });

      try {
        const [collusion, payload] = await Promise.all([
          graphApi.getCollusion(caseId),
          graphApi.getCaseGraph(caseId),
        ]);

        if (cancelled) return;

        const collusionEdges = collusion?.collusion_relationships ?? [];

        if (collusionEdges.length === 0) {
          setState({
            nodes: [],
            edges: [],
            loading: false,
            error: null,
            hasCollusion: false,
          });
          return;
        }

        const nodeByKey = new Map<string, GraphNodeDTO>();
        for (const node of payload?.nodes ?? []) {
          nodeByKey.set(node.business_key, node);
        }

        const involvedKeys = new Set<string>();
        for (const edge of collusionEdges) {
          involvedKeys.add(edge.source);
          involvedKeys.add(edge.target);
        }

        const nodes: GraphNodeDTO[] = [];
        for (const key of involvedKeys) {
          const node = nodeByKey.get(key);
          if (node) {
            nodes.push(node);
          }
        }

        setState({
          nodes,
          edges: collusionEdges,
          loading: false,
          error: null,
          hasCollusion: true,
        });
      } catch (err) {
        if (cancelled) return;

        setState({
          ...EMPTY_STATE,
          loading: false,
          error:
            err instanceof Error
              ? err.message
              : 'Gagal memuat graf kolusi.',
        });
      }
    }

    void load();

    return () => {
      cancelled = true;
    };
  }, [caseId]);

  const elements = useMemo(() => {
    const nodeElements = state.nodes.map((node) => {
      const isSelected = selectedNodeId === node.business_key;
      return {
        data: {
          id: node.business_key,
          label: node.name,
          entity_type: node.entity_type,
        },
        classes: isSelected ? 'selected' : '',
      };
    });

    const edgeElements = state.edges.map((edge, index) => {
      const shared = readSharedPackages(edge);
      const id = edge.id ?? `collusion-${edge.source}-${edge.target}-${index}`;
      return {
        data: {
          id,
          source: edge.source,
          target: edge.target,
          relationship_type: edge.relationship_type,
          label: shared !== null ? `${shared} shared` : undefined,
        },
      };
    });

    return [...nodeElements, ...edgeElements];
  }, [state.nodes, state.edges, selectedNodeId]);

  const stylesheet: cytoscape.StylesheetStyle[] = useMemo(
    () => [
      {
        selector: 'node',
        style: {
          label: 'data(label)',
          color: '#ffffff',
          'font-size': '10px',
          'text-valign': 'center',
          'text-halign': 'center',
          'text-wrap': 'wrap',
          'text-max-width': '90px',
          width: '90px',
          height: '45px',
          shape: 'round-rectangle',
          'border-width': 2,
          'background-color': (ele) =>
            readEntityColor(ele.data('entity_type')),
          'border-color': (ele) =>
            readEntityBorder(ele.data('entity_type')),
        },
      },
      {
        selector: 'node.selected',
        style: {
          'border-width': 4,
          'border-color': '#f8fafc',
        },
      },
      {
        selector: 'edge',
        style: {
          width: 2,
          'line-color': '#dc2626',
          'target-arrow-color': '#dc2626',
          'target-arrow-shape': 'triangle',
          'curve-style': 'bezier',
          label: 'data(label)',
          'font-size': '9px',
          color: '#fca5a5',
          'text-background-color': '#111827',
          'text-background-opacity': 0.8,
          'text-background-padding': '2px',
        },
      },
    ],
    [],
  );

  const layout = useMemo(
    () => ({
      name: 'circle',
      padding: 40,
      animate: false,
    }),
    [],
  );

  const handleCyTap = (event: cytoscape.EventObject) => {
    const target = event.target;
    if (target.isNode && target.isNode()) {
      const nodeId = String(target.data('id') ?? '');
      onNodeSelect?.(nodeId);
    }
  };

  if (state.loading) {
    return (
      <div className="flex items-center justify-center py-12 text-gray-400">
        <div className="mr-2 h-5 w-5 animate-spin rounded-full border-b-2 border-cyan-500" />
        Memuat graf kolusi...
      </div>
    );
  }

  if (state.error) {
    return (
      <div className="rounded-lg border border-red-500/30 bg-red-500/5 p-4 text-sm text-red-300">
        {state.error}
      </div>
    );
  }

  if (!state.hasCollusion) {
    return (
      <div className="rounded-lg border border-gray-700 bg-gray-900/40 p-6 text-center">
        <p className="text-sm text-gray-300">
          Tidak ada pola kolusi terdeteksi untuk kasus ini.
        </p>
        <p className="mt-1 text-xs text-gray-500">
          Graph F3 COLLUSION relationships: 0
        </p>
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-lg border border-gray-700 bg-gray-900">
      <div className="flex items-center justify-between border-b border-gray-700 px-4 py-3">
        <div>
          <h3 className="font-semibold text-white">
            Visualisasi Jaringan Kolusi
          </h3>
          <p className="text-xs text-gray-500">
            {state.nodes.length} entitas · {state.edges.length} hubungan
            COLLUSION
          </p>
        </div>
        <div className="flex items-center gap-3 text-xs text-gray-400">
          <span className="flex items-center gap-1">
            <span className="h-2 w-2 rounded-full bg-emerald-500" />
            Vendor
          </span>
          <span className="flex items-center gap-1">
            <span className="h-2 w-2 rounded-full bg-blue-500" />
            Procurement
          </span>
          <span className="flex items-center gap-1">
            <span className="h-2 w-2 rounded-full bg-amber-500" />
            Institution
          </span>
        </div>
      </div>

      <div style={{ height: '520px', width: '100%' }}>
        <CytoscapeComponent
          elements={elements}
          layout={layout}
          stylesheet={stylesheet}
          style={{ width: '100%', height: '100%', backgroundColor: '#0f172a' }}
          cy={(cy) => {
            cy.removeListener('tap');
            cy.on('tap', 'node', handleCyTap);
          }}
        />
      </div>

      <div className="flex items-center justify-between border-t border-gray-700 px-4 py-2 text-xs text-gray-500">
        <span>{state.nodes.length} node</span>
        <span>{state.edges.length} hubungan COLLUSION</span>
        <span className="text-cyan-400">Klik node untuk detail</span>
      </div>
    </div>
  );
};

export default CollusionGraphVisualization;
