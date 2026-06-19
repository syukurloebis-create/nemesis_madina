import React, { useEffect, useRef, useState } from 'react';
import cytoscape from 'cytoscape';
import { GraphControls } from './GraphControls';
import { EntityDetails } from './EntityDetails';

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

    const filteredNodes = filter
      ? nodes.filter(n => n.label.toLowerCase().includes(filter.toLowerCase()) || n.id.toLowerCase().includes(filter.toLowerCase()))
      : nodes;
    const filteredNodeIds = new Set(filteredNodes.map(n => n.id));
    const filteredEdges = edges.filter(e => filteredNodeIds.has(e.source) && filteredNodeIds.has(e.target));

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
      })),
    ];

    if (cyRef.current) {
      cyRef.current.destroy();
    }

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
          selector: 'edge',
          style: {
            'width': 2,
            'line-color': '#888',
            'target-arrow-color': '#888',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'label': 'data(type)',
            'font-size': '8px',
            'color': '#88aaff',
          },
        },
      ],
      layout: { name: 'grid', animate: true },
    });

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
  }, [nodes, edges, filter, onEntitySelect]);

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
    if (cyRef.current) {
      cyRef.current.layout({ name: layout === 'cola' ? 'grid' : 'grid', animate: true }).run();
    }
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
