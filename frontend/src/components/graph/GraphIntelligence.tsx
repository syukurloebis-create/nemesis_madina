// GraphIntelligence.tsx - Wrapper untuk EnhancedNetworkGraph
import React from 'react';
import { EnhancedNetworkGraph } from '../network/EnhancedNetworkGraph';

interface GraphIntelligenceProps {
  actors: any[];
  height?: number;
  className?: string;
  onNodeClick?: (actor: any) => void;
}

export const GraphIntelligence: React.FC<GraphIntelligenceProps> = ({
  actors,
  height = 350,
  className = '',
  onNodeClick
}) => {
  return (
    <EnhancedNetworkGraph
      actors={actors}
      height={height}
      className={className}
      onNodeClick={onNodeClick}
    />
  );
};

export default GraphIntelligence;
