// src/hooks/useGovernance.ts
import { useQuery } from '@tanstack/react-query';
import { api } from '@/services/api';

export interface DecisionNode {
  id: string;
  type: 'policy' | 'decision' | 'action' | 'review';
  title: string;
  description: string;
  timestamp: string;
  actor: string;
  status: 'active' | 'applied' | 'rejected' | 'pending';
  children?: DecisionNode[];
}

export interface AuditEvent {
  id: string;
  entityId: string;
  action: string;
  policyName: string;
  timestamp: string;
  actor: string;
  details: Record<string, any>;
  status: 'success' | 'failed' | 'pending';
}

export const useDecisionLineage = (entityId: string, limit: number = 50) => {
  return useQuery({
    queryKey: ['decisionLineage', entityId, limit],
    queryFn: () => api.getDecisionLineage(entityId, limit).then(res => res.data),
    enabled: !!entityId,
  });
};

export const useAuditTrail = (entityId: string, startDate?: string, endDate?: string) => {
  return useQuery({
    queryKey: ['auditTrail', entityId, startDate, endDate],
    queryFn: () => api.getAuditTrail(entityId, startDate, endDate).then(res => res.data),
    enabled: !!entityId,
  });
};

export const usePolicyImpact = (policyId: string) => {
  return useQuery({
    queryKey: ['policyImpact', policyId],
    queryFn: () => api.getPolicyImpact(policyId).then(res => res.data),
    enabled: !!policyId,
  });
};