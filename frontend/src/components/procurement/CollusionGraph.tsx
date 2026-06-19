import React, { useEffect, useRef, useState } from 'react';
import CytoscapeComponent from 'react-cytoscapejs';
import cytoscape from 'cytoscape';
import dagre from 'cytoscape-dagre';

// Register layout extension
cytoscape.use(dagre);

interface CollusionGraphProps {
  patterns: Array<{
    id: string;
    type: string;
    entities: string[];
    confidence: number;
    severity: string;
  }>;
  onNodeSelect?: (nodeId: string) => void;
}

export const CollusionGraph: React.FC<CollusionGraphProps> = ({ patterns, onNodeSelect }) => {
  const cyRef = useRef<any>(null);
  const [elements, setElements] = useState<any[]>([]);

  useEffect(() => {
    // Build graph elements from patterns
    const nodes = new Map<string, any>();
    const edges: any[] = [];
    
    patterns.forEach((pattern, idx) => {
      // Add pattern as a node
      const patternId = `pattern-${pattern.id}`;
      nodes.set(patternId, {
        data: {
          id: patternId,
          label: pattern.type,
          type: 'pattern',
          confidence: pattern.confidence,
          severity: pattern.severity
        }
      });
      
      // Add entity nodes and edges
      pattern.entities.forEach((entity, entityIdx) => {
        const entityId = `entity-${entity.replace(/\s/g, '-')}`;
        if (!nodes.has(entityId)) {
          nodes.set(entityId, {
            data: {
              id: entityId,
              label: entity,
              type: 'entity',
              riskScore: pattern.confidence
            }
          });
        }
        
        // Add edge between pattern and entity
        edges.push({
          data: {
            id: `edge-${pattern.id}-${entityIdx}`,
            source: patternId,
            target: entityId,
            label: 'terlibat'
          }
        });
      });
    });
    
    setElements([...Array.from(nodes.values()), ...edges]);
  }, [patterns]);

  const layout = {
    name: 'dagre',
    rankDir: 'TB',
    spacingFactor: 1.5,
    animate: true,
    animationDuration: 500
  };

  const stylesheet = [
    {
      selector: 'node',
      style: {
        'background-color': '#1f2937',
        'label': 'data(label)',
        'color': '#ffffff',
        'font-size': '10px',
        'text-valign': 'center',
        'text-halign': 'center',
        'width': '80px',
        'height': '40px',
        'border-width': '2px',
        'border-color': '#374151',
        'shape': 'roundrectangle'
      }
    },
    {
      selector: 'node[type="pattern"]',
      style: {
        'background-color': '#0e2b3d',
        'border-color': '#06b6d4',
        'width': '100px',
        'height': '50px'
      }
    },
    {
      selector: 'node[type="entity"]',
      style: {
        'background-color': '#1e3a2f',
        'border-color': '#10b981',
        'width': '90px',
        'height': '40px'
      }
    },
    {
      selector: 'edge',
      style: {
        'width': 2,
        'line-color': '#6b7280',
        'target-arrow-color': '#6b7280',
        'target-arrow-shape': 'triangle',
        'curve-style': 'bezier',
        'label': 'data(label)',
        'font-size': '8px',
        'color': '#9ca3af'
      }
    }
  ];

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-700">
        <h3 className="font-semibold text-white">Visualisasi Jaringan Kolusi</h3>
        <p className="text-xs text-gray-500 mt-1">
          Hubungan antar entitas dalam pola kolusi pengadaan
        </p>
      </div>
      
      <div style={{ height: '400px', width: '100%' }}>
        {elements.length > 0 ? (
          <CytoscapeComponent
            elements={elements}
            layout={layout}
            stylesheet={stylesheet}
            style={{ width: '100%', height: '100%' }}
            cy={(cy) => {
              cyRef.current = cy;
              cy.on('tap', 'node', (evt) => {
                const node = evt.target;
                onNodeSelect?.(node.data('id'));
              });
            }}
          />
        ) : (
          <div className="flex items-center justify-center h-full text-gray-500">
            <p>Belum ada data kolusi untuk divisualisasikan</p>
          </div>
        )}
      </div>
      
      <div className="px-4 py-2 border-t border-gray-700 flex justify-between text-xs text-gray-500">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 bg-cyan-800 rounded"></div>
            <span>Pola Kolusi</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 bg-green-800 rounded"></div>
            <span>Entitas</span>
          </div>
        </div>
        <span>{elements.length} node, {patterns.length} pola</span>
      </div>
    </div>
  );
};
