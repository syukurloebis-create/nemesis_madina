// src/components/network/VendorNetworkGraph.tsx
import React, { useMemo } from 'react';

interface VendorNode {
  id: string;
  name: string;
  risk_score: number;
  connections: number;
  cluster_id?: number;
}

interface VendorEdge {
  source: string;
  target: string;
  relationship_type: string;
  weight: number;
}

interface VendorNetworkGraphProps {
  nodes: VendorNode[];
  edges: VendorEdge[];
  onNodeClick?: (node: VendorNode) => void;
  className?: string;
}

export const VendorNetworkGraph: React.FC<VendorNetworkGraphProps> = ({
  nodes = [],
  edges = [],
  onNodeClick,
  className = '',
}) => {
  const [selectedNode, setSelectedNode] = React.useState<string | null>(null);

  if (nodes.length === 0) {
    return (
      <div className={`bg-dark-card rounded-xl shadow-lg border border-gray-700/50 p-6 ${className}`}>
        <p className="text-gray-400 text-center">Tidak ada data jaringan</p>
      </div>
    );
  }

  // Hitung node dengan degree tertinggi
  const topNodes = useMemo(() => {
    return [...nodes]
      .sort((a, b) => b.connections - a.connections)
      .slice(0, 10);
  }, [nodes]);

  // Filter edges untuk top nodes
  const topNodeIds = useMemo(() => {
    return new Set(topNodes.map(n => n.id));
  }, [topNodes]);

  const relevantEdges = useMemo(() => {
    return edges.filter(e => 
      topNodeIds.has(e.source) || topNodeIds.has(e.target)
    );
  }, [edges, topNodeIds]);

  const getNodeColor = (node: VendorNode) => {
    if (node.risk_score >= 80) return 'border-red-500 bg-red-500/10';
    if (node.risk_score >= 60) return 'border-orange-500 bg-orange-500/10';
    return 'border-green-500 bg-green-500/10';
  };

  const getEdgeColor = (edge: VendorEdge) => {
    if (edge.relationship_type === 'shared_package') return 'border-blue-500/50';
    if (edge.relationship_type === 'vendor_similarity') return 'border-purple-500/50';
    return 'border-gray-500/50';
  };

  return (
    <div className={`bg-dark-card rounded-xl shadow-lg border border-gray-700/50 p-4 ${className}`}>
      <h3 className="text-sm font-semibold text-white mb-3">🌐 Jaringan Vendor</h3>
      
      {/* Legend */}
      <div className="flex flex-wrap gap-3 mb-3 text-xs">
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded-full border-2 border-red-500"></span>
          <span className="text-gray-400">High Risk</span>
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded-full border-2 border-orange-500"></span>
          <span className="text-gray-400">Medium Risk</span>
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded-full border-2 border-blue-500"></span>
          <span className="text-gray-400">Shared Package</span>
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded-full border-2 border-purple-500"></span>
          <span className="text-gray-400">Similarity</span>
        </span>
      </div>

      {/* Network Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
        {topNodes.map((node) => (
          <div
            key={node.id}
            onClick={() => {
              setSelectedNode(node.id);
              onNodeClick?.(node);
            }}
            className={`border-2 rounded-lg p-3 cursor-pointer transition hover:scale-105 ${getNodeColor(node)}`}
          >
            <p className="text-white text-sm font-medium truncate" title={node.name}>
              {node.name}
            </p>
            <div className="flex justify-between text-xs text-gray-400 mt-1">
              <span>Risk: {node.risk_score}%</span>
              <span>Conn: {node.connections}</span>
            </div>
            {node.cluster_id !== undefined && (
              <span className="text-[10px] text-gray-500">Cluster: {node.cluster_id}</span>
            )}
          </div>
        ))}
      </div>

      {/* Edges Info */}
      <div className="mt-4 text-xs text-gray-500">
        <p>Menampilkan {topNodes.length} dari {nodes.length} vendor</p>
        <p>{relevantEdges.length} hubungan terlihat</p>
      </div>
    </div>
  );
};
