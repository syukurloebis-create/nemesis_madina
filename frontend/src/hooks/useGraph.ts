/**
 * useGraph Hook - NO TYPE IMPORTS
 * Use any to avoid Vite import issues
 */

import { useState, useEffect, useCallback } from 'react';
import { graphApi } from '../services/api/graph';

export function useGraph(options: any = {}) {
  const { autoRefresh = false, refreshInterval = 30000, caseId } = options;
  
  const [entities, setEntities] = useState<any[]>([]);
  const [relationships, setRelationships] = useState<any[]>([]);
  const [metrics, setMetrics] = useState<any>(null);
  const [communities, setCommunities] = useState<any[]>([]);
  const [keyActors, setKeyActors] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const [entitiesData, relationshipsData, metricsData, communitiesData, actorsData] = await Promise.all([
        graphApi.getEntities({ case_id: caseId }),
        graphApi.getRelationships({ case_id: caseId }),
        graphApi.getMetrics(caseId),
        graphApi.getCommunities(caseId),
        graphApi.getKeyActors(20),
      ]);

      setEntities(entitiesData || []);
      setRelationships(relationshipsData || []);
      setMetrics(metricsData);
      setCommunities(communitiesData || []);
      setKeyActors(actorsData || []);
    } catch (err: any) {
      const errorMsg = err.message || 'Failed to load graph data';
      setError(errorMsg);
      console.error('useGraph error:', err);
    } finally {
      setLoading(false);
    }
  }, [caseId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  useEffect(() => {
    if (!autoRefresh) return;
    const interval = setInterval(fetchData, refreshInterval);
    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, fetchData]);

  return {
    entities,
    relationships,
    metrics,
    communities,
    keyActors,
    loading,
    error,
    refresh: fetchData,
  };
}

export default useGraph;