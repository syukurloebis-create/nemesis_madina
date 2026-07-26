import { useState, useEffect, useCallback } from 'react';
import { api } from '../services/api';

export interface DashboardData {
  health: any;
  cases: any;
  fraud: any;
  graph: any;
  risk: any;
  executive: any;
  strategic: any;
  intelligence: any;
  graphRisk: any;
  keyActors: any[];
}

export function useDashboardData(caseId?: string) {
  const [data, setData] = useState<DashboardData>({
    health: null,
    cases: null,
    fraud: null,
    graph: null,
    risk: null,
    executive: null,
    strategic: null,
    intelligence: null,
    graphRisk: null,
    keyActors: [],
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const isStale = false;

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    const params = caseId ? { case_id: caseId } : undefined;
    try {
      const [health, cases, fraud, graph, risk] = await Promise.all([
        api.get('/health'),
        api.get('/api/v1/cases/stats', { params }),
        api.get('/api/v1/fraud/stats', { params }),
        api.get('/api/v1/graph/metrics', { params }),
        api.get('/api/v1/risk/stats', { params }),
      ]);

      const healthData = health?.data || health || {};
      const casesData = cases?.data || cases || {};
      const fraudData = fraud?.data || fraud || {};
      const graphData = graph?.data || graph || {};
      const riskData = risk?.data || risk || {};

      setData({
        health: healthData,
        cases: casesData,
        fraud: fraudData,
        graph: graphData,
        risk: riskData,
        executive: {
          totalCases: casesData.total || 0,
          activeCases: casesData.open || 0,
          criticalAlerts: fraudData.active_alerts || 0,
          riskScore: riskData.total_risk || 0,
        },
        strategic: {
          totalEntities: graphData.total_entities || 0,
          totalRelationships: graphData.total_relationships || 0,
        },
        intelligence: {
          riskScore: riskData.total_risk || 0,
          fraudScore: fraudData.high_confidence || 0,
          graphScore: graphData.total_relationships || 0,
          confidence: 0,
          reasoning: [],
        },
        graphRisk: {
          score: 0,
          entities: graphData.total_entities || 0,
          relationships: graphData.total_relationships || 0,
          collusion: graphData.collusion_edges || 0,
          centrality: 0,
        },
        keyActors: [],
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  }, [caseId]);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, [fetchData]);

  return {
    data,
    health: data.health,
    cases: data.cases,
    fraud: data.fraud,
    graph: data.graph,
    risk: data.risk,
    loading,
    error,
    isLoading: loading,
    isError: !!error,
    refresh: fetchData,
    refetch: fetchData,
    isStale,
  };
}

export default useDashboardData;
