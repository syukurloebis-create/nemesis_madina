import { useQuery } from '@tanstack/react-query';
import { api } from '@/services/api';

export interface GraphNode {
  id: string;
  label: string;
  type: 'entity' | 'vendor' | 'opd' | 'user' | 'collusion';
  trustScore: number;
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  size: number;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  type: 'endorses' | 'transacts' | 'delegates' | 'colludes';
  weight: number;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export const useEntityGraph = (entityId: string, depth: number = 2) => {
  return useQuery({
    queryKey: ['entityGraph', entityId, depth],
    queryFn: () => api.getEntityGraph(entityId, depth).then(res => res.data),
    enabled: !!entityId,
  });
};

export const useCollusionCycles = (minCycle: number = 3, maxCycle: number = 6) => {
  return useQuery({
    queryKey: ['collusionCycles', minCycle, maxCycle],
    queryFn: () => api.getCollusionCycles(minCycle, maxCycle).then(res => res.data),
    refetchInterval: 60000,
  });
};
