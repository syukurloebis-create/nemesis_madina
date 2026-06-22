/**
 * useCases Hook
 */

import { useState, useEffect, useCallback } from 'react';
import { casesApi } from '../services/api/cases';
import type { Case, CaseStats, RiskExplanation } from '../services/api/cases';

export interface UseCasesOptions {
  autoRefresh?: boolean;
  refreshInterval?: number;
}

export function useCases(options: UseCasesOptions = {}) {
  const { autoRefresh = false, refreshInterval = 30000 } = options;
  
  const [cases, setCases] = useState<Case[]>([]);
  const [stats, setStats] = useState<CaseStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [riskExplanations, setRiskExplanations] = useState<Record<string, RiskExplanation[]>>({});

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const [casesData, statsData] = await Promise.all([
        casesApi.getAll(),
        casesApi.getStats(),
      ]);

      setCases(casesData);
      setStats(statsData);

      // Fetch risk explanations for each case
      const explanations: Record<string, RiskExplanation[]> = {};
      for (const caseItem of casesData) {
        try {
          const exp = await casesApi.getRiskExplanations(caseItem.id);
          explanations[caseItem.id] = exp;
        } catch {
          explanations[caseItem.id] = [];
        }
      }
      setRiskExplanations(explanations);
    } catch (err: any) {
      setError(err.message || 'Failed to load cases');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  useEffect(() => {
    if (!autoRefresh) return;
    const interval = setInterval(fetchData, refreshInterval);
    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval, fetchData]);

  return {
    cases,
    stats,
    riskExplanations,
    loading,
    error,
    refresh: fetchData,
  };
}

export default useCases;