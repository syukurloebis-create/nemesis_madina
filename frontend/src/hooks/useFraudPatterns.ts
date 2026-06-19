// hooks/useFraudPatterns.ts - Custom hook for fraud patterns
import { useState, useEffect, useCallback } from 'react';
import { FraudPattern, FraudPatternSummary } from '../types/fraud';
import fraudApi from '../services/fraudApi';

interface UseFraudPatternsReturn {
  patterns: FraudPattern[];
  summary: FraudPatternSummary | null;
  loading: boolean;
  error: string | null;
  fetchPatterns: () => Promise<void>;
  updateStatus: (id: string, status: string) => Promise<void>;
  investigatePattern: (id: string) => Promise<void>;
}

export const useFraudPatterns = (): UseFraudPatternsReturn => {
  const [patterns, setPatterns] = useState<FraudPattern[]>([]);
  const [summary, setSummary] = useState<FraudPatternSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchPatterns = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [patternsData, summaryData] = await Promise.all([
        fraudApi.getPatterns(),
        fraudApi.getPatternSummary()
      ]);
      
      setPatterns(patternsData);
      setSummary(summaryData);
    } catch (err: any) {
      console.error('❌ Error fetching fraud patterns:', err);
      setError(err.response?.data?.detail || 'Gagal memuat data pola fraud');
    } finally {
      setLoading(false);
    }
  }, []);

  const updateStatus = useCallback(async (id: string, status: string) => {
    try {
      const updated = await fraudApi.updatePatternStatus(id, status);
      setPatterns(prev => prev.map(p => p.id === id ? updated : p));
      // Refresh summary
      const summaryData = await fraudApi.getPatternSummary();
      setSummary(summaryData);
    } catch (err: any) {
      console.error('❌ Error updating pattern status:', err);
      throw err;
    }
  }, []);

  const investigatePattern = useCallback(async (id: string) => {
    try {
      await fraudApi.investigatePattern(id);
      // Refresh data
      await fetchPatterns();
    } catch (err: any) {
      console.error('❌ Error investigating pattern:', err);
      throw err;
    }
  }, [fetchPatterns]);

  useEffect(() => {
    fetchPatterns();
  }, [fetchPatterns]);

  return {
    patterns,
    summary,
    loading,
    error,
    fetchPatterns,
    updateStatus,
    investigatePattern
  };
};

export default useFraudPatterns;
