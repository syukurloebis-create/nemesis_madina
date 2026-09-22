import React, { useCallback, useMemo, useRef, useState } from 'react';
import CytoscapeComponent from 'react-cytoscapejs';
import cytoscape, { Core, ElementDefinition, EventObjectNode } from 'cytoscape';
import dagre from 'cytoscape-dagre';

import graphApi from '../../services/api/graph';
import type {
  GraphEdgeDTO,
  GraphNodeDTO,
  GraphPayload,
} from '../../services/api/graph';

import GraphControls, {
  EntityTypeFilter,
  LayoutType,
  RelationshipTypeFilter,
} from './GraphControls';
import EntityDetails from './EntityDetails';
import cytoscapeStyles from './cytoscapeStyles';

cytoscape.use(dagre);

const INITIAL_MAX_NODES = 200;
const FILTERED_MAX_NODES = 500;

interface GraphVisualizationProps {
  caseId: string;
  initialFilters?: {
    entityTypes?: EntityTypeFilter[];
    relationshipTypes?: RelationshipTypeFilter[];
  };
  onNodeSelect?: (node: GraphNodeDTO | null) => void;
}

interface GraphState {
  payload: GraphPayload | null;
  loading: boolean;
  error: string | null;
}

const ENTITY_TYPE_PRIORITY: Record<string, number> = {
  vendor: 0,
  procurement_record: 1,
};

function getEntityTypePriority(type: string): number {
  return ENTITY_TYPE_PRIORITY[type] ?? 99;
}

function getNodeId(node: GraphNodeDTO): string {
  return node.business_key;
}

function getEdgeSource(edge: GraphEdgeDTO): string {
  return String((edge as GraphEdgeDTO & { source?: string }).source ?? '');
}

function getEdgeTarget(edge: GraphEdgeDTO): string {
  return String((edge as GraphEdgeDTO & { target?: string }).target ?? '');
}

function getRelationshipType(edge: GraphEdgeDTO): string {
  return String(
    (edge as GraphEdgeDTO & {
      relationship_type?: string;
      type?: string;
    }).relationship_type ??
      (edge as GraphEdgeDTO & { type?: string }).type ??
      '',
  );
}

function buildDegreeMap(
  nodes: GraphNodeDTO[],
  edges: GraphEdgeDTO[],
): Map<string, number> {
  const degrees = new Map<string, number>();

  for (const node of nodes) {
    degrees.set(getNodeId(node), 0);
  }

  for (const edge of edges) {
    const source = getEdgeSource(edge);
    const target = getEdgeTarget(edge);

    if (degrees.has(source)) {
      degrees.set(source, (degrees.get(source) ?? 0) + 1);
    }

    if (degrees.has(target)) {
      degrees.set(target, (degrees.get(target) ?? 0) + 1);
    }
  }

  return degrees;
}

function selectProgressiveNodes(
  nodes: GraphNodeDTO[],
  edges: GraphEdgeDTO[],
  maxNodes: number,
): GraphNodeDTO[] {
  if (nodes.length <= maxNodes) {
    return nodes;
  }

  const degreeMap = buildDegreeMap(nodes, edges);

  const sorted = [...nodes].sort((a, b) => {
    const typePriority =
      getEntityTypePriority(a.entity_type) -
      getEntityTypePriority(b.entity_type);

    if (typePriority !== 0) {
      return typePriority;
    }

    const degreeDifference =
      (degreeMap.get(getNodeId(b)) ?? 0) -
      (degreeMap.get(getNodeId(a)) ?? 0);

    if (degreeDifference !== 0) {
      return degreeDifference;
    }

    return a.name.localeCompare(b.name);
  });

  // Preserve both canonical entity types when possible.
  const vendors = sorted.filter(
    (node) => node.entity_type === 'vendor',
  );
  const procurement = sorted.filter(
    (node) => node.entity_type === 'procurement_record',
  );

  if (vendors.length > 0 && procurement.length > 0 && maxNodes >= 2) {
    const vendorQuota = Math.min(
      vendors.length,
      Math.ceil(maxNodes / 2),
    );
    const procurementQuota = Math.min(
      procurement.length,
      maxNodes - vendorQuota,
    );

    const selected = [
      ...vendors.slice(0, vendorQuota),
      ...procurement.slice(0, procurementQuota),
    ];

    if (selected.length < maxNodes) {
      const selectedIds = new Set(
        selected.map((node) => getNodeId(node)),
      );

      for (const node of sorted) {
        if (selected.length >= maxNodes) {
          break;
        }

        if (!selectedIds.has(getNodeId(node))) {
          selected.push(node);
          selectedIds.add(getNodeId(node));
        }
      }
    }

    return selected;
  }

  return sorted.slice(0, maxNodes);
}

function buildElements(
  nodes: GraphNodeDTO[],
  edges: GraphEdgeDTO[],
): ElementDefinition[] {
  const nodeIds = new Set(nodes.map(getNodeId));

  const nodeElements: ElementDefinition[] = nodes.map((node) => ({
    data: {
      id: getNodeId(node),
      business_key: node.business_key,
      name: node.name,
      entity_type: node.entity_type,
      source_id: node.source_id,
      extra_data: node.extra_data,
    },
  }));

  const edgeElements: ElementDefinition[] = [];

  for (const edge of edges) {
    const source = getEdgeSource(edge);
    const target = getEdgeTarget(edge);

    if (!source || !target) {
      continue;
    }

    if (!nodeIds.has(source) || !nodeIds.has(target)) {
      continue;
    }

    const relationshipType = getRelationshipType(edge);

    edgeElements.push({
      data: {
        id:
          edge.id ??
          `${source}:${relationshipType}:${target}`,
        source,
        target,
        relationship_type: relationshipType,
      },
    });
  }

  return [...nodeElements, ...edgeElements];
}

const GraphVisualization: React.FC<GraphVisualizationProps> = ({
  caseId,
  initialFilters,
  onNodeSelect,
}) => {
  const cyRef = useRef<Core | null>(null);

  const [state, setState] = useState<GraphState>({
    payload: null,
    loading: true,
    error: null,
  });

  const [entityTypes, setEntityTypes] = useState<EntityTypeFilter[]>(
    initialFilters?.entityTypes ?? ['vendor', 'procurement_record'],
  );

  const [relationshipTypes, setRelationshipTypes] =
    useState<RelationshipTypeFilter[]>(
      initialFilters?.relationshipTypes ?? [
        'VENDOR_HAS_PACKAGE',
        'COLLUSION',
      ],
    );

  const [layout, setLayout] = useState<LayoutType>('dagre');
  const [search, setSearch] = useState('');
  const [showAll, setShowAll] = useState(false);

  const [selectedNode, setSelectedNode] =
    useState<GraphNodeDTO | null>(null);

  const loadGraph = useCallback(async () => {
    if (!caseId) {
      setState({
        payload: null,
        loading: false,
        error: 'Case ID tidak tersedia.',
      });
      return;
    }

    setState((previous) => ({
      ...previous,
      loading: true,
      error: null,
    }));

    try {
      const response = await graphApi.getCaseGraph(caseId);

      setState({
        payload: response,
        loading: false,
        error: null,
      });
    } catch (error) {
      const message =
        error instanceof Error
          ? error.message
          : 'Gagal memuat graph intelligence.';

      setState({
        payload: null,
        loading: false,
        error: message,
      });
    }
  }, [caseId]);

  React.useEffect(() => {
    void loadGraph();
  }, [loadGraph]);

  const filteredNodes = useMemo(() => {
    const nodes = state.payload?.nodes ?? [];

    return nodes.filter((node) =>
      entityTypes.includes(node.entity_type as EntityTypeFilter),
    );
  }, [state.payload, entityTypes]);

  const filteredEdges = useMemo(() => {
    const edges = state.payload?.edges ?? [];

    return edges.filter((edge) =>
      relationshipTypes.includes(
        getRelationshipType(edge) as RelationshipTypeFilter,
      ),
    );
  }, [state.payload, relationshipTypes]);

  const degreeMap = useMemo(
    () => buildDegreeMap(filteredNodes, filteredEdges),
    [filteredNodes, filteredEdges],
  );

  const displayedNodes = useMemo(
    () =>
      selectProgressiveNodes(
        filteredNodes,
        filteredEdges,
        showAll ? FILTERED_MAX_NODES : INITIAL_MAX_NODES,
      ),
    [filteredNodes, filteredEdges, showAll],
  );

  const displayedElements = useMemo(
    () => buildElements(displayedNodes, filteredEdges),
    [displayedNodes, filteredEdges],
  );

  const searchMatches = useMemo(() => {
    const query = search.trim().toLowerCase();

    if (!query) {
      return new Set<string>();
    }

    return new Set(
      displayedNodes
        .filter((node) => {
          const businessKey = node.business_key.toLowerCase();
          const name = node.name.toLowerCase();
          const type = node.entity_type.toLowerCase();

          return (
            businessKey.includes(query) ||
            name.includes(query) ||
            type.includes(query)
          );
        })
        .map(getNodeId),
    );
  }, [displayedNodes, search]);

  const cyElements = useMemo(
    () =>
      displayedElements.map((element) => {
        if (!element.data?.id) {
          return element;
        }

        const id = String(element.data.id);

        if (searchMatches.has(id)) {
          return {
            ...element,
            classes: 'search-match',
          };
        }

        return element;
      }),
    [displayedElements, searchMatches],
  );

  const applyLayout = useCallback(
    (cy: Core, selectedLayout: LayoutType = layout) => {
      const layoutConfig =
        selectedLayout === 'dagre'
          ? {
              name: 'dagre',
              rankDir: 'LR',
              nodeSep: 40,
              rankSep: 90,
              animate: false,
              fit: true,
              padding: 30,
            }
          : {
              name: 'circle',
              animate: false,
              fit: true,
              padding: 30,
            };

      cy.layout(layoutConfig).run();
    },
    [layout],
  );

  const handleCyInit = useCallback(
    (cy: Core) => {
      cyRef.current = cy;

      cy.on('tap', 'node', (event: EventObjectNode) => {
        const data = event.target.data();

        const entity = displayedNodes.find(
          (node) => getNodeId(node) === data.id,
        );

        if (!entity) {
          return;
        }

        setSelectedNode(entity);
        onNodeSelect?.(entity);
      });

      cy.on('mouseover', 'node', (event: EventObjectNode) => {
        const node = event.target;
        const degree = degreeMap.get(String(node.id())) ?? 0;

        node.data('degree', degree);
      });

      applyLayout(cy);
    },
    [applyLayout, degreeMap, displayedNodes, onNodeSelect],
  );

  React.useEffect(() => {
    const cy = cyRef.current;

    if (!cy) {
      return;
    }

    applyLayout(cy);
  }, [applyLayout, cyElements]);

  const handleZoomIn = () => {
    const cy = cyRef.current;

    if (!cy) {
      return;
    }

    cy.zoom({
      level: cy.zoom() * 1.2,
      renderedPosition: {
        x: cy.width() / 2,
        y: cy.height() / 2,
      },
    });
  };

  const handleZoomOut = () => {
    const cy = cyRef.current;

    if (!cy) {
      return;
    }

    cy.zoom({
      level: cy.zoom() / 1.2,
      renderedPosition: {
        x: cy.width() / 2,
        y: cy.height() / 2,
      },
    });
  };

  const handleFit = () => {
    cyRef.current?.fit(undefined, 30);
  };

  const handleReset = () => {
    const cy = cyRef.current;

    if (!cy) {
      return;
    }

    setSearch('');
    cy.elements().removeClass('search-match');
    cy.zoom(1);
    cy.pan({ x: 0, y: 0 });
    applyLayout(cy);
  };

  const handleNodeClose = () => {
    setSelectedNode(null);
    onNodeSelect?.(null);
  };

  const availableEntityTypes = useMemo(
    () =>
      Array.from(
        new Set(
          (state.payload?.nodes ?? []).map(
            (node) => node.entity_type,
          ),
        ),
      ) as EntityTypeFilter[],
    [state.payload],
  );

  const availableRelationshipTypes = useMemo(
    () =>
      Array.from(
        new Set(
          (state.payload?.edges ?? []).map(
            getRelationshipType,
          ),
        ),
      ) as RelationshipTypeFilter[],
    [state.payload],
  );

  if (state.loading) {
    return (
      <div className="flex items-center justify-center min-h-[500px] text-gray-400">
        Memuat Graph Intelligence…
      </div>
    );
  }

  if (state.error) {
    return (
      <div className="rounded-xl border border-red-500/30 bg-red-500/5 p-6">
        <div className="text-red-400 font-semibold">
          Graph Intelligence gagal dimuat
        </div>
        <div className="text-gray-400 text-sm mt-2">
          {state.error}
        </div>

        <button
          type="button"
          onClick={() => void loadGraph()}
          className="mt-4 px-4 py-2 rounded-lg bg-gray-700 hover:bg-gray-600 text-white text-sm"
        >
          Coba Lagi
        </button>
      </div>
    );
  }

  if (!state.payload) {
    return (
      <div className="flex items-center justify-center min-h-[500px] text-gray-400">
        Data Graph tidak tersedia.
      </div>
    );
  }

  return (
    <div className="relative w-full min-h-[650px] rounded-xl overflow-hidden border border-gray-700 bg-gray-950">
      <GraphControls
        entityTypes={entityTypes}
        relationshipTypes={relationshipTypes}
        availableEntityTypes={availableEntityTypes}
        availableRelationshipTypes={availableRelationshipTypes}
        layout={layout}
        search={search}
        showAll={showAll}
        nodeCount={displayedNodes.length}
        totalNodeCount={filteredNodes.length}
        onEntityTypesChange={setEntityTypes}
        onRelationshipTypesChange={setRelationshipTypes}
        onLayoutChange={(nextLayout) => {
          setLayout(nextLayout);

          requestAnimationFrame(() => {
            if (cyRef.current) {
              applyLayout(cyRef.current, nextLayout);
            }
          });
        }}
        onSearchChange={setSearch}
        onShowAllChange={setShowAll}
        onZoomIn={handleZoomIn}
        onZoomOut={handleZoomOut}
        onFit={handleFit}
        onReset={handleReset}
      />

      <div className="absolute inset-x-0 bottom-0 top-[112px]">
        <CytoscapeComponent
          elements={cyElements}
          stylesheet={cytoscapeStyles}
          style={{
            width: '100%',
            height: '100%',
            minHeight: '540px',
          }}
          cy={handleCyInit}
          wheelSensitivity={0.2}
          minZoom={0.15}
          maxZoom={4}
          boxSelectionEnabled={false}
          autoungrabify={false}
        />
      </div>

      <div className="absolute left-4 bottom-4 z-10 px-3 py-2 rounded-lg bg-gray-900/90 border border-gray-700 text-xs text-gray-400">
        Menampilkan {displayedNodes.length} dari {filteredNodes.length}{' '}
        node terfilter · {filteredEdges.length} relasi terfilter
      </div>

      {selectedNode && (
        <EntityDetails
          entity={selectedNode}
          degree={degreeMap.get(getNodeId(selectedNode)) ?? 0}
          onClose={handleNodeClose}
        />
      )}
    </div>
  );
};

export default GraphVisualization;
