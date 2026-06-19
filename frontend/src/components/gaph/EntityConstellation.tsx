# src/components/graph/EntityConstellation.tsx
import React, { useEffect, useRef } from 'react';
import CytoscapeComponent from 'react-cytoscapejs';
import cytoscape from 'cytoscape';
import cola from 'cytoscape-cola';

// Register cola layout for force-directed graph
cytoscape.use(cola);

interface Entity {
  id: string;
  type: string;
  trustScore: number;
  riskLevel: 'low' | 'medium' | 'high';
}

interface Relationship {
  source: string;
  target: string;
  type: string;
  weight: number;
}

interface EntityConstellationProps {
  entities: Entity[];
  relationships: Relationship[];
}

export const EntityConstellation: React.FC<EntityConstellationProps> = ({ entities, relationships }) => {
  const elements = [
    ...entities.map(entity => ({
      data: {
        id: entity.id,
        label: entity.id.slice(0, 12),
        type: entity.type,
        trustScore: entity.trustScore,
        riskLevel: entity.riskLevel,
      },
      style: {
        'background-color': 
          entity.riskLevel === 'high' ? '#ff4444' :
          entity.riskLevel === 'medium' ? '#ffaa00' : '#00ff88',
        'width': 40 + (1 - entity.trustScore) * 60,
        'height': 40 + (1 - entity.trustScore) * 60,
        'label': 'data(label)',
      },
    })),
    ...relationships.map(rel => ({
      data: {
        id: `${rel.source}-${rel.target}`,
        source: rel.source,
        target: rel.target,
        label: rel.type,
        weight: rel.weight,
      },
      style: {
        'width': 2 + rel.weight * 3,
        'line-color': '#00ffff',
        'target-arrow-color': '#00ffff',
        'target-arrow-shape': 'triangle',
        'curve-style': 'bezier',
        'opacity': 0.6 + rel.weight * 0.4,
      },
    })),
  ];

  const layout = {
    name: 'cola',
    animate: true,
    maxSimulationTime: 2000,
    edgeLength: (edge: any) => {
      return 100 / (edge.data('weight') + 0.5);
    },
    nodeSpacing: 50,
    infinite: false,
  };

  const stylesheet = [
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
        'border-color': '#00ffff',
      },
    },
    {
      selector: 'node[riskLevel="high"]',
      style: {
        'border-color': '#ff4444',
        'border-width': 3,
        'animation': 'pulse 1s infinite',
      },
    },
    {
      selector: 'edge',
      style: {
        'width': 'data(width)',
        'line-color': 'data(line-color)',
        'target-arrow-color': 'data(target-arrow-color)',
        'target-arrow-shape': 'data(target-arrow-shape)',
        'curve-style': 'data(curve-style)',
        'label': 'data(label)',
        'font-size': '8px',
        'text-rotation': 'autorotate',
        'color': '#88aaff',
      },
    },
  ];

  return (
    <div className="bg-gray-900 rounded-xl border border-purple-500/30 overflow-hidden" style={{ height: '600px' }}>
      <div className="p-4 border-b border-gray-800">
        <h3 className="text-lg font-semibold text-purple-400 flex items-center gap-2">
          🌌 Entity Constellation Map
        </h3>
        <p className="text-xs text-gray-500 mt-1">Force-directed relationship intelligence graph</p>
      </div>
      <CytoscapeComponent
        elements={elements}
        layout={layout}
        stylesheet={stylesheet}
        style={{ width: '100%', height: 'calc(100% - 60px)', backgroundColor: '#0a0a1a' }}
        cy={(cy) => {
          cy.on('tap', 'node', (evt) => {
            const node = evt.target;
            console.log('Selected entity:', node.data('id'));
          });
        }}
      />
    </div>
  );
};