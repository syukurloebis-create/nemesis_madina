// src/components/graph/CollusionGraph.tsx
import React, { useEffect, useRef, useState } from 'react';
import cytoscape from 'cytoscape';
import cola from 'cytoscape-cola';
import dagre from 'cytoscape-dagre';
import { GraphControls } from './GraphControls';
import { EntityDetails } from './EntityDetails';

// Register layouts
cytoscape.use(cola);
cytoscape.use(dagre);

interface Node {
  id: string;
  label: string;
  type: string;
  trustScore: number;
  riskLevel: string;
  size: number;
}

interface Edge {
  id: string;
  source: string;
  target: string;
  type: string;
  weight: number;
}

interface CollusionGraphProps {
  nodes: Node[];
  edges: Edge[];
  onEntitySelect?: (entityId: string) => void;
}

export const CollusionGraph: React.FC<CollusionGraphProps> = ({ nodes, edges, onEntitySelect }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<cytoscape.Core | null>(null);
  const [selectedEntity, setSelectedEntity] = useState<Node | null>(null);
  const [currentLayout, setCurrentLayout] = useState<'cola' | 'dagre' | 'circle'>('cola');
  const [filter, setFilter] = useState('');

  const getNodeColor = (type: string, riskLevel: string) => {
    if (riskLevel === 'critical') return '#ff4444';
    if (riskLevel === 'high') return '#ff8844';
    if (riskLevel === 'medium') return '#ffaa44';
    if (riskLevel === 'collusion') return '#ff00ff';
    if (type === 'vendor') return '#00ffff';
    if (type === 'opd') return '#44aaff';
    if (type === 'user') return '#88ff88';
    return '#aaaaaa';
  };

  useEffect(() => {
    if (!containerRef.current || nodes.length === 0) return;

    // Filter nodes by search term
    const filteredNodes = filter
      ? nodes.filter(n => n.label.toLowerCase().includes(filter.toLowerCase()) || n.id.toLowerCase().includes(filter.toLowerCase()))
      : nodes;
    const filteredNodeIds = new Set(filteredNodes.map(n => n.id));
    const filteredEdges = edges.filter(e => filteredNodeIds.has(e.source) && filteredNodeIds.has(e.target));

    // Prepare elements
    const elements = [
      ...filteredNodes.map(node => ({
        data: {
          id: node.id,
          label: node.label,
          type: node.type,
          trustScore: node.trustScore,
          riskLevel: node.riskLevel,
        },
        style: {
          'background-color': getNodeColor(node.type, node.riskLevel),
          'width': node.size,
          'height': node.size,
          'label': node.label.length > 15 ? node.label.slice(0, 12) + '...' : node.label,
        },
      })),
      ...filteredEdges.map(edge => ({
        data: {
          id: edge.id,
          source: edge.source,
          target: edge.target,
          type: edge.type,
          weight: edge.weight,
        },
        style: {
          'width': 1 + edge.weight * 2,
          'line-color': '#888',
          'target-arrow-color': '#888',
          'target-arrow-shape': 'triangle',
          'curve-style': 'bezier',
          'opacity': 0.6 + edge.weight * 0.4,
        },
      })),
    ];

    // Destroy existing graph
    if (cyRef.current) {
      cyRef.current.destroy();
    }

    // Create new graph
    const cy = cytoscape({
      container: containerRef.current,
      elements,
      style: [
        {
          selector: 'node',
          style: {
            'background-color': 'data(background-color)',
            'width': 'data(width)',
            'height': 'data(height)',
            'label': 'data(label)',
            'color': '#ffffff',
            'font-size': '10px',
            'text-valign': 'center',
            'text-halign': 'center',
            'border-width': 2,
            'border-color': '#fff',
            'border-opacity': 0.5,
          },
        },
        {
          selector: 'node[riskLevel="critical"]',
          style: {
            'border-color': '#ff4444',
            'border-width': 3,
            'animation': 'pulse 1s infinite',
          },
        },
        {
          selector: 'node[riskLevel="high"]',
          style: { 'border-color': '#ff8844', 'border-width': 2 },
        },
        {
          selector: 'node[type="collusion"]',
          style: { 'background-color': '#ff00ff', 'border-color': '#ff00ff' },
        },
        {
          selector: 'edge',
          style: {
            'width': 'data(width)',
            'line-color': 'data(line-color)',
            'target-arrow-color': 'data(target-arrow-color)',
            'target-arrow-shape': 'data(target-arrow-shape)',
            'curve-style': 'data(curve-style)',
            'label': 'data(type)',
            'font-size': '8px',
            'text-rotation': 'autorotate',
            'color': '#88aaff',
          },
        },
        {
          selector: 'edge[type="colludes"]',
          style: { 'line-color': '#ff4444', 'target-arrow-color': '#ff4444' },
        },
        {
          selector: 'edge[weight="high"]',
          style: { 'line-color': '#ffaa44', 'width': 4 },
        },
      ],
      layout: {
        name: currentLayout === 'cola' ? 'cola' : currentLayout === 'dagre' ? 'dagre' : 'circle',
        animate: true,
        ...(currentLayout === 'cola' && { maxSimulationTime: 2000, edgeLength: 80 }),
        ...(currentLayout === 'dagre' && { rankDir: 'LR' }),
      },
    });

    // Add hover effects
    cy.on('mouseover', 'node', (evt) => {
      const node = evt.target;
      node.style({
        'border-width': 4,
        'border-color': '#00ffff',
        'font-size': '12px',
      });
    });

    cy.on('mouseout', 'node', (evt) => {
      const node = evt.target;
      node.style({
        'border-width': 2,
        'border-color': '#fff',
        'font-size': '10px',
      });
    });

    // Click handler
    cy.on('tap', 'node', (evt) => {
      const node = evt.target;
      const nodeData = node.data();
      const selected = nodes.find(n => n.id === nodeData.id);
      if (selected) {
        setSelectedEntity(selected);
        if (onEntitySelect) onEntitySelect(selected.id);
      }
    });

    cyRef.current = cy;

    // Fit to viewport
    setTimeout(() => {
      cy.fit();
      cy.center();
    }, 100);

    return () => {
      if (cyRef.current) {
        cyRef.current.destroy();
        cyRef.current = null;
      }
    };
  }, [nodes, edges, currentLayout, filter, onEntitySelect]);

  const handleZoomIn = () => {
    if (cyRef.current) {
      const zoom = cyRef.current.zoom();
      cyRef.current.zoom(zoom * 1.2);
    }
  };

  const handleZoomOut = () => {
    if (cyRef.current) {
      const zoom = cyRef.current.zoom();
      cyRef.current.zoom(zoom * 0.8);
    }
  };

  const handleFit = () => {
    if (cyRef.current) {
      cyRef.current.fit();
      cyRef.current.center();
    }
  };

  const handleReset = () => {
    if (cyRef.current) {
      cyRef.current.zoom(1);
      cyRef.current.center();
      setCurrentLayout('cola');
    }
  };

  const handleLayoutChange = (layout: 'cola' | 'dagre' | 'circle') => {
    setCurrentLayout(layout);
  };

  if (nodes.length === 0) {
    return (
      <div className="bg-gray-900/50 rounded-xl p-12 text-center border border-gray-800">
        <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gray-800 flex items-center justify-center">
          <svg className="w-8 h-8 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M12 5l7 7-7 7" />
          </svg>
        </div>
        <p className="text-gray-400">No graph data available</p>
        <p className="text-xs text-gray-500 mt-1">Select an entity or wait for collusion detection</p>
      </div>
    );
  }

  return (
    <div className="relative bg-gray-900/95 rounded-xl border border-purple-500/30 overflow-hidden" style={{ height: '600px' }}>
      <GraphControls
        onZoomIn={handleZoomIn}
        onZoomOut={handleZoomOut}
        onFit={handleFit}
        onReset={handleReset}
        onLayoutChange={handleLayoutChange}
        onFilterChange={setFilter}
        currentLayout={currentLayout}
      />
      <div ref={containerRef} style={{ width: '100%', height: '100%' }} />
      <div className="absolute bottom-4 left-4 z-10 bg-gray-900/80 backdrop-blur rounded-lg px-3 py-1.5 text-xs text-gray-400">
        {nodes.length} nodes • {edges.length} edges
      </div>
      <EntityDetails entity={selectedEntity} onClose={() => setSelectedEntity(null)} />
    </div>
  );
};