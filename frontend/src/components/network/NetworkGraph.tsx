// NetworkGraph.tsx - Fixed with proper exports
import React, { useCallback, useMemo } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  addEdge,
  MarkerType,
} from 'reactflow';
import type { Connection } from 'reactflow';
import 'reactflow/dist/style.css';

interface Actor {
  id?: string;
  name: string;
  risk_score: number;
  connections?: number;
  connection_type?: string;
  community?: string;
  trust_score?: number;
}

interface NetworkGraphProps {
  actors: Actor[];
  className?: string;
  height?: number | string;
  onNodeClick?: (actor: Actor) => void;
}

// Custom Node Component
const ActorNode = ({ data }: { data: any }) => {
  const getRiskColor = (score: number) => {
    if (score >= 80) return { bg: '#fef2f2', border: '#ef4444', text: '#dc2626' };
    if (score >= 60) return { bg: '#fffbeb', border: '#f59e0b', text: '#d97706' };
    if (score >= 40) return { bg: '#eff6ff', border: '#3b82f6', text: '#2563eb' };
    return { bg: '#f0fdf4', border: '#22c55e', text: '#16a34a' };
  };

  const colors = getRiskColor(data.risk_score || 0);
  
  return (
    <div
      style={{
        background: colors.bg,
        border: `2px solid ${colors.border}`,
        borderRadius: '8px',
        padding: '12px 16px',
        width: '180px',
        cursor: 'pointer',
        boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
      }}
      className="hover:shadow-lg hover:scale-105 transition-all"
    >
      <div style={{ fontWeight: 600, fontSize: '14px', color: colors.text }}>
        {data.label}
      </div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '6px' }}>
        <span style={{ fontSize: '12px', color: '#6b7280' }}>
          Risk: {data.risk_score || 0}
        </span>
        <span style={{ fontSize: '12px', color: '#6b7280' }}>
          {data.connections || 0} connections
        </span>
      </div>
      {data.community && data.community !== 'unclassified' && (
        <div style={{ 
          fontSize: '10px', 
          color: '#9ca3af', 
          marginTop: '4px',
          background: '#f3f4f6',
          padding: '2px 8px',
          borderRadius: '12px',
          display: 'inline-block'
        }}>
          {data.community}
        </div>
      )}
    </div>
  );
};

export const NetworkGraph: React.FC<NetworkGraphProps> = ({
  actors,
  className = '',
  height = 450,
  onNodeClick,
}) => {
  const nodeTypes = useMemo(() => ({
    actor: ActorNode,
  }), []);

  const initialNodes = useMemo(() => {
    if (!actors || actors.length === 0) return [];
    
    return actors.slice(0, 15).map((actor, index) => {
      const riskScore = actor.risk_score || 0;
      const total = Math.min(actors.length, 15);
      const angle = (index / total) * 2 * Math.PI - Math.PI / 2;
      const radius = Math.min(200 + (total - 5) * 15, 400);
      
      return {
        id: actor.id || `actor-${index}`,
        type: 'actor',
        position: {
          x: 400 + radius * Math.cos(angle),
          y: 250 + radius * Math.sin(angle) * 0.7,
        },
        data: {
          label: actor.name,
          risk_score: riskScore,
          connections: actor.connections || 0,
          community: actor.community || 'unclassified',
        },
      };
    });
  }, [actors]);

  const initialEdges = useMemo(() => {
    if (!actors || actors.length < 2) return [];
    
    const edges: any[] = [];
    const actorList = actors.slice(0, 15);
    
    actorList.forEach((actor, index) => {
      if (index < actorList.length - 1) {
        const nextActor = actorList[index + 1];
        const isConnected = (actor.connections || 0) > 0 && (nextActor.connections || 0) > 0;
        
        edges.push({
          id: `edge-${index}`,
          source: actor.id || `actor-${index}`,
          target: nextActor.id || `actor-${index + 1}`,
          animated: isConnected,
          style: {
            stroke: isConnected ? '#3b82f6' : '#9ca3af',
            strokeWidth: isConnected ? 2 : 1,
          },
          markerEnd: {
            type: MarkerType.ArrowClosed,
            color: isConnected ? '#3b82f6' : '#9ca3af',
          },
          label: isConnected ? (actor.connection_type || 'terhubung') : '',
        });
      }
    });
    
    return edges;
  }, [actors]);

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  React.useEffect(() => {
    setNodes(initialNodes);
    setEdges(initialEdges);
  }, [actors, initialNodes, initialEdges, setNodes, setEdges]);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge({
      ...params,
      animated: true,
      style: { stroke: '#3b82f6', strokeWidth: 2 },
      markerEnd: { type: MarkerType.ArrowClosed, color: '#3b82f6' },
    }, eds)),
    [setEdges]
  );

  const onNodeClickHandler = useCallback(
    (_event: React.MouseEvent, node: any) => {
      const actor = actors.find(a => (a.id || a.name) === node.id || a.name === node.data.label);
      if (onNodeClick && actor) {
        onNodeClick(actor);
      }
    },
    [actors, onNodeClick]
  );

  if (!actors || actors.length === 0) {
    return (
      <div className="bg-white dark:bg-dark-card rounded-lg shadow p-6 text-center text-gray-500 dark:text-gray-400">
        <p className="text-lg">🌐</p>
        <p>Tidak ada data actor</p>
      </div>
    );
  }

  return (
    <div className={`bg-white dark:bg-dark-card rounded-lg shadow p-4 ${className}`}>
      <div className="flex justify-between items-center mb-3">
        <h3 className="text-lg font-bold">🌐 Network Intelligence</h3>
        <div className="flex gap-3 text-xs text-gray-500">
          <span>{actors.length} actors</span>
          <span>{edges.length} connections</span>
        </div>
      </div>
      
      <div style={{ height: typeof height === 'number' ? height : 450 }}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onNodeClick={onNodeClickHandler}
          nodeTypes={nodeTypes}
          fitView
          attributionPosition="bottom-right"
          minZoom={0.5}
          maxZoom={1.5}
        >
          <Background variant="dots" gap={16} size={1.5} color="#e5e7eb" />
          <Controls showInteractive={false} />
          <MiniMap 
            nodeColor={(n) => {
              const risk = n.data?.risk_score || 0;
              if (risk >= 80) return '#ef4444';
              if (risk >= 60) return '#f97316';
              if (risk >= 40) return '#eab308';
              return '#22c55e';
            }}
          />
        </ReactFlow>
      </div>
    </div>
  );
};

export default NetworkGraph;
