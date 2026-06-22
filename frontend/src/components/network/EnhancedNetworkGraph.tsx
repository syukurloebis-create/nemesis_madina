// src/components/network/EnhancedNetworkGraph.tsx
import React from 'react';

interface NetworkNode {
  id: string;
  name: string;
  risk_score?: number;
  connections?: number;
}

interface EnhancedNetworkGraphProps {
  data: NetworkNode[];
  className?: string;
  height?: number;
  onNodeClick?: (node: NetworkNode) => void;
}

export const EnhancedNetworkGraph: React.FC<EnhancedNetworkGraphProps> = ({
  data = [],
  className = '',
  height = 400,
  onNodeClick,
}) => {
  if (!data || data.length === 0) {
    return (
      <div className={`bg-dark-card rounded-xl shadow-lg border border-gray-700/50 p-6 ${className}`}>
        <p className="text-gray-400 text-center">Tidak ada data jaringan</p>
      </div>
    );
  }

  return (
    <div className={`bg-dark-card rounded-xl shadow-lg border border-gray-700/50 p-4 ${className}`}>
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
        {data.slice(0, 10).map((node) => (
          <div
            key={node.id}
            onClick={() => onNodeClick?.(node)}
            className="bg-dark-bg border border-gray-700/50 rounded-lg p-3 hover:border-blue-500/50 transition cursor-pointer"
          >
            <p className="text-white text-sm font-medium truncate" title={node.name}>
              {node.name || 'Tidak Diketahui'}
            </p>
            <div className="flex justify-between text-xs text-gray-400 mt-1">
              <span>Risiko: {node.risk_score ?? 0}%</span>
              <span>Koneksi: {node.connections ?? 0}</span>
            </div>
          </div>
        ))}
      </div>
      {data.length > 10 && (
        <p className="text-xs text-gray-500 text-center mt-4">
          Menampilkan 10 dari {data.length} aktor
        </p>
      )}
    </div>
  );
};

export default EnhancedNetworkGraph;
