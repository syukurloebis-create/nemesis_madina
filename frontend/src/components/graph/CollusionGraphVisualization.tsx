import React, { useEffect, useState } from 'react';
import CytoscapeComponent from 'react-cytoscapejs';
import cytoscape from 'cytoscape';
import { useAuthStore } from '../../stores/authStore';
import { api } from '../../services/api';

interface CollusionNode {
  id: string;
  label: string;
  type: 'vendor' | 'person' | 'institution';
  riskScore: number;
}

interface CollusionEdge {
  id: string;
  source: string;
  target: string;
  label: string;
  confidence: number;
}

interface CollusionGraphProps {
  caseId?: string;
  onNodeSelect?: (nodeId: string) => void;
}

export const CollusionGraphVisualization: React.FC<CollusionGraphProps> = ({ 
  caseId, 
  onNodeSelect 
}) => {
  const { token } = useAuthStore();
  const [elements, setElements] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);

  useEffect(() => {
    const fetchGraphData = async () => {
      if (!token) return;
      
      try {
        // Fetch entities and relationships
        const entities = await api.getEntities(caseId || '');
        const collusions = await api.request('/vendors/collusions');
        
        const nodes: CollusionNode[] = [];
        const edges: CollusionEdge[] = [];
        
        // Add entities as nodes
        (entities || []).forEach((entity: any) => {
          nodes.push({
            id: entity.id,
            label: entity.name,
            type: entity.entity_type === 'vendor' ? 'vendor' : 
                   entity.entity_type === 'person' ? 'person' : 'institution',
            riskScore: entity.risk_score || 0
          });
        });
        
        // Add collusion patterns as edges
        (collusions || []).forEach((pattern: any, idx: number) => {
          const patternId = `pattern-${idx}`;
          nodes.push({
            id: patternId,
            label: pattern.type,
            type: 'institution',
            riskScore: pattern.confidence
          });
          
          pattern.entities.forEach((entity: string) => {
            const entityNode = nodes.find(n => n.label === entity);
            if (entityNode) {
              edges.push({
                id: `edge-${patternId}-${entityNode.id}`,
                source: patternId,
                target: entityNode.id,
                label: 'terlibat',
                confidence: pattern.confidence
              });
            }
          });
        });
        
        // Build cytoscape elements
        const cyElements = [
          ...nodes.map(node => ({
            data: {
              id: node.id,
              label: node.label,
              type: node.type,
              riskScore: node.riskScore
            },
            style: {
              'background-color': node.type === 'vendor' ? '#1e3a2f' :
                               node.type === 'person' ? '#0e2b3d' : '#3d2a1e',
              'border-color': node.riskScore > 70 ? '#ef4444' :
                              node.riskScore > 40 ? '#f59e0b' : '#10b981',
              'border-width': 2
            }
          })),
          ...edges.map(edge => ({
            data: {
              id: edge.id,
              source: edge.source,
              target: edge.target,
              label: `${edge.label} (${edge.confidence}%)`
            },
            style: {
              'line-color': '#6b7280',
              'target-arrow-color': '#6b7280',
              'target-arrow-shape': 'triangle',
              'curve-style': 'bezier',
              'width': 2
            }
          }))
        ];
        
        setElements(cyElements);
      } catch (err) {
        console.error('Failed to fetch graph data:', err);
        // Demo data
        setElements([
          { data: { id: 'pt-maju', label: 'PT. Maju Jaya', type: 'vendor' } },
          { data: { id: 'cv-karya', label: 'CV. Karya Mandiri', type: 'vendor' } },
          { data: { id: 'pt-bangun', label: 'PT. Bangun Nusantara', type: 'vendor' } },
          { data: { id: 'kementerian', label: 'Kementerian PUPR', type: 'institution' } },
          { data: { id: 'pattern1', label: 'Vendor Address Collusion', type: 'pattern' } },
          { data: { source: 'pattern1', target: 'pt-maju', label: 'terlibat' } },
          { data: { source: 'pattern1', target: 'cv-karya', label: 'terlibat' } },
          { data: { source: 'pt-maju', target: 'pt-bangun', label: 'subkontrak' } }
        ]);
      } finally {
        setLoading(false);
      }
    };
    
    fetchGraphData();
  }, [caseId, token]);

  const layout = {
    name: 'cose',
    idealEdgeLength: 100,
    nodeOverlap: 20,
    refresh: 20,
    fit: true,
    padding: 30,
    randomize: true,
    componentSpacing: 100,
    nodeRepulsion: 400000,
    edgeElasticity: 100,
    nestingFactor: 5,
    gravity: 80,
    numIter: 1000,
    initialTemp: 200,
    coolingFactor: 0.95,
    minTemp: 1.0
  };

  const stylesheet = [
    {
      selector: 'node',
      style: {
        'label': 'data(label)',
        'color': '#ffffff',
        'font-size': '10px',
        'text-valign': 'center',
        'text-halign': 'center',
        'width': '80px',
        'height': '40px',
        'border-width': '2px',
        'shape': 'roundrectangle'
      }
    },
    {
      selector: 'node[type="vendor"]',
      style: {
        'background-color': '#1e3a2f',
        'border-color': '#10b981'
      }
    },
    {
      selector: 'node[type="person"]',
      style: {
        'background-color': '#0e2b3d',
        'border-color': '#06b6d4'
      }
    },
    {
      selector: 'node[type="institution"]',
      style: {
        'background-color': '#3d2a1e',
        'border-color': '#f59e0b'
      }
    },
    {
      selector: 'node[type="pattern"]',
      style: {
        'background-color': '#4c1d95',
        'border-color': '#a855f7',
        'width': '100px',
        'height': '50px'
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

  if (loading) {
    return (
      <div className="flex justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-500"></div>
        <span className="ml-2 text-gray-400">Memuat graf kolusi...</span>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-700 flex justify-between items-center">
        <div>
          <h3 className="font-semibold text-white">Visualisasi Jaringan Kolusi</h3>
          <p className="text-xs text-gray-500">Hubungan antar entitas dalam pola kolusi</p>
        </div>
        <div className="flex items-center space-x-3 text-xs">
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 rounded bg-green-800"></div>
            <span className="text-gray-400">Vendor</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 rounded bg-cyan-800"></div>
            <span className="text-gray-400">Orang</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 rounded bg-purple-800"></div>
            <span className="text-gray-400">Pola Kolusi</span>
          </div>
        </div>
      </div>
      
      <div style={{ height: '500px', width: '100%' }}>
        <CytoscapeComponent
          elements={elements}
          layout={layout}
          stylesheet={stylesheet}
          style={{ width: '100%', height: '100%', backgroundColor: '#1f2937' }}
          cy={(cy) => {
            cy.on('tap', 'node', (evt) => {
              const node = evt.target;
              const nodeId = node.data('id');
              setSelectedNode(nodeId);
              onNodeSelect?.(nodeId);
            });
          }}
        />
      </div>
      
      <div className="px-4 py-2 border-t border-gray-700 flex justify-between text-xs text-gray-500">
        <span>{elements.filter((e: any) => e.data.source === undefined).length} node</span>
        <span>{elements.filter((e: any) => e.data.source !== undefined).length} hubungan</span>
        <span className="text-cyan-400">Klik node untuk detail</span>
      </div>
    </div>
  );
};
