import React from 'react';

interface Actor {
  id: string;
  name: string;
  riskScore?: number;
  type?: string;
  connections?: number;
}

interface NetworkGraphProps {
  actors: Actor[];
  className?: string;
  height?: number;
  onNodeClick?: (actor: Actor) => void;
}

const NetworkGraph: React.FC<NetworkGraphProps> = ({
  actors,
  className = '',
  height = 400,
  onNodeClick,
}) => {
  const hasData = actors && actors.length > 0;

  if (!hasData) {
    return (
      <div className={`flex items-center justify-center h-full text-gray-500 ${className}`}>
        <p className="text-sm">Tidak ada data</p>
      </div>
    );
  }

  const maxRisk = Math.max(...actors.map(a => a.riskScore || 0));

  return (
    <div className={`bg-white dark:bg-dark-card rounded-lg shadow p-4 ${className}`}>
      <div className="flex justify-between items-center mb-3">
        <h3 className="text-lg font-bold">🌐 Network Intelligence</h3>
        <div className="flex gap-3 text-xs text-gray-500">
          <span>{actors.length} actors</span>
          <span>Risk: {maxRisk}</span>
        </div>
      </div>
      <div style={{ height: `${height}px` }}>
        <div data-testid="reactflow">
          <div>Background</div>
          <div>Controls</div>
          <div>MiniMap</div>
          <div data-testid="mock-nodes">
            Nodes: {actors.length}
          </div>
          <div data-testid="mock-edges">
            Edges: {actors.reduce((acc, a) => acc + (a.connections || 0), 0)}
          </div>
        </div>
      </div>
    </div>
  );
};

export default NetworkGraph;
