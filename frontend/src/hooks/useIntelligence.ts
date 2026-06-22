// src/hooks/useIntelligence.ts
import { useState, useEffect, useCallback } from 'react';
import { intelligenceService } from '@/services/intelligenceService';
import { IUnifiedIntelligence } from '@/types/intelligence';

interface IUseIntelligenceResult {
  data: IUnifiedIntelligence | null;
  loading: boolean;
  error: Error | null;
  refresh: () => Promise<void>;
  isStale: boolean;
}

export const useIntelligence = (caseId: string): IUseIntelligenceResult => {
  const [data, setData] = useState<IUnifiedIntelligence | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [isStale, setIsStale] = useState(false);

  const fetchIntelligence = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await intelligenceService.getUnifiedIntelligence(caseId);
      setData(result);
      setIsStale(false);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }, [caseId]);

  // Initial fetch
  useEffect(() => {
    fetchIntelligence();
  }, [fetchIntelligence]);

  // Auto-refresh every 5 minutes
  useEffect(() => {
    const interval = setInterval(() => {
      setIsStale(true);
    }, 4.5 * 60 * 1000); // 4.5 minutes

    return () => clearInterval(interval);
  }, []);

  return { data, loading, error, refresh: fetchIntelligence, isStale };
};