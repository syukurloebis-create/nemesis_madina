// src/hooks/useFraudPatterns.ts
import { useState, useEffect, useCallback } from 'react';
import fraudApi from '../services/fraudApi';
import type { FraudPattern, FraudSeverity, FraudStatus } from '../types';

interface UseFraudPatternsOptions {
  caseId?: string;
  severity?: FraudSeverity;
  status?: FraudStatus;
  autoFetch?: boolean;
}

export const useFraudPatterns = (options: UseFraudPatternsOptions = {}) => {
  const { caseId, severity, status, autoFetch = true } = options;
  const [patterns, setPatterns] = useState<FraudPattern[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchPatterns = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fraudApi.getFraudPatterns(caseId || '');
      let data = response.data || [];
      if (severity) data = data.filter((p: FraudPattern) => p.severity === severity);
      if (status) data = data.filter((p: FraudPattern) => p.status === status);
      setPatterns(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch fraud patterns');
    } finally {
      setLoading(false);
    }
  }, [caseId, severity, status]);

  useEffect(() => {
    if (autoFetch) fetchPatterns();
  }, [autoFetch, fetchPatterns]);

  return { patterns, loading, error, refetch: fetchPatterns };
};

export default useFraudPatterns;
