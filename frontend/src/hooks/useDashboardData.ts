import { useState, useEffect, useCallback } from 'react';
import { dashboardApi } from '../services/dashboardApi';

interface DashboardData {
  executive: any;
  stats: any;
  cases: any;
  evidence: any;
  risk: any;
  actors: any;
  recommendations: any;
}

export const useDashboardData = (caseId: string) => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const [
        executive,
        stats,
        cases,
        evidence,
        risk,
        actors,
        recommendations
      ] = await Promise.all([
        dashboardApi.getExecutive().catch(() => ({ data: null })),
        dashboardApi.getStats().catch(() => ({ data: null })),
        dashboardApi.getCases().catch(() => ({ data: null })),
        dashboardApi.getEvidenceStats().catch(() => ({ data: null })),
        dashboardApi.getRiskTrend().catch(() => ({ data: null })),
        dashboardApi.getKeyActors().catch(() => ({ data: null })),
        dashboardApi.getRecommendations().catch(() => ({ data: null })),
      ]);

      setData({
        executive: executive.data,
        stats: stats.data,
        cases: cases.data,
        evidence: evidence.data,
        risk: risk.data,
        actors: actors.data,
        recommendations: recommendations.data,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Gagal memuat data dashboard');
    } finally {
      setLoading(false);
    }
  }, [caseId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, loading, error, refresh: fetchData };
};
