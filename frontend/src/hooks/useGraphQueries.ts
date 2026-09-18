import { useQuery } from '@tanstack/react-query';
import {
  graphApi,
  GraphSummary,
  GraphMetrics,
  KeyActor,
  GraphPayload,
} from '@/services/api/graph';

export function useGraphSummary(caseId: string | undefined) {
  return useQuery<GraphSummary>({
    queryKey: ['graph', 'summary', caseId],
    queryFn: () => graphApi.getSummary(caseId!),
    enabled: !!caseId,
  });
}

export function useGraphMetrics(caseId: string | undefined) {
  return useQuery<GraphMetrics>({
    queryKey: ['graph', 'metrics', caseId],
    queryFn: () => graphApi.getMetrics(caseId!),
    enabled: !!caseId,
  });
}

export function useGraphKeyActors(
  caseId: string | undefined,
  limit = 20,
) {
  return useQuery<{
    case_id: string;
    actors: KeyActor[];
    count: number;
  }>({
    queryKey: ['graph', 'key-actors', caseId, limit],
    queryFn: () => graphApi.getKeyActors(caseId!, limit),
    enabled: !!caseId,
  });
}

export function useGraphFull(
  caseId: string | undefined,
  enabled: boolean,
) {
  return useQuery<GraphPayload>({
    queryKey: ['graph', 'full', caseId],
    queryFn: () => graphApi.getCaseGraph(caseId!),
    enabled: !!caseId && enabled,
    staleTime: 5 * 60_000,
  });
}
