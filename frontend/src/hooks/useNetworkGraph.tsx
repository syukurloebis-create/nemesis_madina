// useNetworkGraph.ts - Network graph logic
import { useState, useEffect, useCallback } from 'react';

interface Actor {
  id?: string;
  name: string;
  risk_score: number;
  connections?: number;
  connection_type?: string;
  community?: string;
}

interface Node {
  id: string;
  type: string;
  data: {
    label: string;
    risk_score: number;
    connections: number;
    community?: string;
  };
  position: { x: number; y: number };
  style: any;
}

interface Edge {
  id: string;
  source: string;
  target: string;
  animated: boolean;
  style: { stroke: string };
  label?: string;
}

export const useNetworkGraph = (actors: Actor[]) => {
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);

  const buildGraph = useCallback(() => {
    if (!actors || actors.length === 0) {
      setNodes([]);
      setEdges([]);
      return;
    }

    // Build nodes
    const actorNodes: Node[] = actors.slice(0, 10).map((actor, index) => {
      const riskScore = actor.risk_score || 0;
      const isHighRisk = riskScore > 70;
      
      return {
        id: actor.id || `actor-${index}`,
        type: 'default',
        data: {
          label: actor.name,
          risk_score: riskScore,
          connections: actor.connections || 0,
          community: actor.community || 'unknown',
        },
        position: {
          x: 100 + Math.random() * 600,
          y: 50 + Math.random() * 300,
        },
        style: {
          background: isHighRisk ? '#fef2f2' : '#eff6ff',
          borderColor: isHighRisk ? '#ef4444' : '#3b82f6',
          borderWidth: 2,
          padding: 12,
          borderRadius: 8,
          width: 180,
          height: 70,
        },
      };
    });

    // Build edges (real connections if available)
    const actorEdges: Edge[] = [];
    actors.slice(0, 10).forEach((actor, index) => {
      if (index < actors.length - 1) {
        const nextActor = actors[index + 1];
        const isConnected = actor.connections && actor.connections > 0;
        
        actorEdges.push({
          id: `edge-${index}`,
          source: actor.id || `actor-${index}`,
          target: nextActor.id || `actor-${index + 1}`,
          animated: isConnected || false,
          style: { 
            stroke: isConnected ? '#3b82f6' : '#9ca3af',
            strokeWidth?: isConnected ? 2 : 1,
          },
          label: actor.connection_type || (isConnected ? 'terhubung' : ''),
        });
      }
    });

    setNodes(actorNodes);
    setEdges(actorEdges);
  }, [actors]);

  useEffect(() => {
    buildGraph();
  }, [buildGraph]);

  return { nodes, edges, setNodes, setEdges };
};

export default useNetworkGraph;
