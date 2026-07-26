// src/hooks/useDecisions.ts
import { useState, useEffect, useCallback } from 'react';
import decisionApi from '../services/decisionApi';
import type { Decision, DecisionTrace } from '../types/decision';

interface UseDecisionsReturn {
  decisions: Decision[];
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
  getDecision: (id: string) => Promise<Decision | null>;
  getTrace: (id: string) => Promise<DecisionTrace[]>;
  createDecision: (data: Partial<Decision>) => Promise<Decision>;
  updateStatus: (id: string, status: Decision['status']) => Promise<Decision>;
}

export const useDecisions = (caseId: string): UseDecisionsReturn => {
  const [decisions, setDecisions] = useState<Decision[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchDecisions = useCallback(async () => {
    if (!caseId) {
      setDecisions([]);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await decisionApi.getDecisions(caseId);
      setDecisions(response.data || []);
    } catch (err) {
      console.error('Error fetching decisions:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch decisions');
      setDecisions([]);
    } finally {
      setLoading(false);
    }
  }, [caseId]);

  const getDecision = useCallback(async (id: string) => {
    try {
      const response = await decisionApi.getDecision(id);
      return response.data || null;
    } catch (err) {
      console.error('Error fetching decision:', err);
      return null;
    }
  }, []);

  const getTrace = useCallback(async (id: string) => {
    try {
      const response = await decisionApi.getDecisionTrace(id);
      return response.data || [];
    } catch (err) {
      console.error('Error fetching decision trace:', err);
      return [];
    }
  }, []);

  const createDecision = useCallback(async (data: Partial<Decision>) => {
    try {
      const response = await decisionApi.createDecision(data);
      await fetchDecisions(); // Refresh list
      return response.data;
    } catch (err) {
      console.error('Error creating decision:', err);
      throw err;
    }
  }, [fetchDecisions]);

  const updateStatus = useCallback(async (id: string, status: Decision['status']) => {
    try {
      const response = await decisionApi.updateDecisionStatus(id, status);
      setDecisions((prev) =>
        prev.map((d) => (d.id === id ? { ...d, status } : d))
      );
      return response.data;
    } catch (err) {
      console.error('Error updating decision status:', err);
      throw err;
    }
  }, []);

  useEffect(() => {
    if (caseId) {
      fetchDecisions();
    }
  }, [caseId, fetchDecisions]);

  return {
    decisions,
    loading,
    error,
    refetch: fetchDecisions,
    getDecision,
    getTrace,
    createDecision,
    updateStatus,
  };
};

export default useDecisions;
