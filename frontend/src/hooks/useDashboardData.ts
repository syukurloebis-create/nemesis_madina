import { useState, useEffect, useCallback } from 'react';
import { dashboardService } from '../services/dashboard';

export interface DashboardData {
  executive: {
    totalCases: number;
    activeCases: number;
    highRiskCases: number;
    criticalAlerts: number;
    avgResolutionTime: number;
    riskScore: number;
  };
  stats: any;
  cases: any[];
  evidence: any;
  risk: any;
  actors: any[];
  recommendations: any[];
  graph?: any;
  rup?: any;
  systemStatus?: any;
}

export const useDashboardData = (caseId: string) => {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isStale, setIsStale] = useState(false);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    setIsStale(false);

    try {
      const dashboardData = await dashboardService.getDashboardData(caseId);
      setData(dashboardData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Gagal memuat data dashboard');
    } finally {
      setLoading(false);
    }
  }, [caseId]);

  useEffect(() => {
    fetchData();
    
    const interval = setInterval(() => {
      setIsStale(true);
      setTimeout(() => {
        fetchData();
      }, 30000);
    }, 4.5 * 60 * 1000);

    return () => clearInterval(interval);
  }, [fetchData]);

  return { data, loading, error, refresh: fetchData, isStale };
};

export default useDashboardData;
