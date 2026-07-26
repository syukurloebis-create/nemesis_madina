import { useEffect, useState, useCallback } from 'react';
import intelligenceService, {
  HealthResponse,
  CaseStats,
  FraudStats,
  GraphMetrics,
  RiskStats,
} from '../services/intelligence';

interface DashboardData {
  health: HealthResponse | null;
  cases: CaseStats | null;
  fraud: FraudStats | null;
  graph: GraphMetrics | null;
  risk: RiskStats | null;
}

interface UseDashboardReturn {
  data: DashboardData;
  loading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
  isRefreshing: boolean;
}

export function useDashboard(): UseDashboardReturn {
  const [data, setData] = useState<DashboardData>({
    health: null,
    cases: null,
    fraud: null,
    graph: null,
    risk: null,
  });
  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setIsRefreshing(true);
      const [health, cases, fraud, graph, risk] = await Promise.all([
        intelligenceService.getHealth(),
        intelligenceService.getCaseStats(),
        intelligenceService.getFraudStats(),
        intelligenceService.getGraphMetrics(),
        intelligenceService.getRiskStats(),
      ]);

      setData({ health, cases, fraud, graph, risk });
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to fetch dashboard data'));
      console.error('Dashboard error:', err);
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchData();

    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, [fetchData]);

  return {
    data,
    loading,
    error,
    refetch: fetchData,
    isRefreshing,
  };
}

export default useDashboard;