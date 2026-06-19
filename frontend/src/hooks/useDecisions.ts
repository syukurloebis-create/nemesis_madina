// hooks/useDecisions.ts - Custom hook for decisions
import { useState, useEffect, useCallback } from 'react';
import { Decision, DecisionSummary, DecisionStatus } from '../types/decision';
import decisionApi from '../services/decisionApi';

interface UseDecisionsReturn {
  decisions: Decision[];
  summary: DecisionSummary | null;
  loading: boolean;
  error: string | null;
  fetchDecisions: () => Promise<void>;
  updateStatus: (id: string, status: DecisionStatus) => Promise<void>;
  executeDecision: (id: string) => Promise<void>;
}

export const useDecisions = (caseId?: string): UseDecisionsReturn => {
  const [decisions, setDecisions] = useState<Decision[]>([]);
  const [summary, setSummary] = useState<DecisionSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDecisions = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [decisionsData, summaryData] = await Promise.all([
        decisionApi.getDecisions(caseId),
        decisionApi.getDecisionSummary()
      ]);
      
      setDecisions(decisionsData);
      setSummary(summaryData);
    } catch (err: any) {
      console.error('❌ Error fetching decisions:', err);
      setError(err.response?.data?.detail || 'Gagal memuat data keputusan');
    } finally {
      setLoading(false);
    }
  }, [caseId]);

  const updateStatus = useCallback(async (id: string, status: DecisionStatus) => {
    try {
      const updated = await decisionApi.updateDecisionStatus(id, status);
      setDecisions(prev => prev.map(d => d.id === id ? updated : d));
      // Refresh summary
      const summaryData = await decisionApi.getDecisionSummary();
      setSummary(summaryData);
    } catch (err: any) {
      console.error('❌ Error updating decision status:', err);
      throw err;
    }
  }, []);

  const executeDecision = useCallback(async (id: string) => {
    try {
      await decisionApi.executeDecision(id);
      // Refresh data
      await fetchDecisions();
    } catch (err: any) {
      console.error('❌ Error executing decision:', err);
      throw err;
    }
  }, [fetchDecisions]);

  useEffect(() => {
    fetchDecisions();
  }, [fetchDecisions]);

  return {
    decisions,
    summary,
    loading,
    error,
    fetchDecisions,
    updateStatus,
    executeDecision
  };
};

export default useDecisions;
