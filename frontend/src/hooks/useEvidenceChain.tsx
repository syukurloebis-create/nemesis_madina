// src/hooks/useEvidenceChain.ts
import { useState, useEffect, useCallback } from 'react';
import evidenceApi from '../services/evidenceApi';
import type { Evidence, CustodyRecord, EvidenceStats } from '../types';

interface UseEvidenceChainReturn {
  evidence: Evidence | null;
  chain: CustodyRecord[];
  stats: EvidenceStats | null;
  loading: boolean;
  error: string | null;
  fetchEvidence: (id: string) => Promise<void>;
  verifyEvidence: (id: string) => Promise<void>;
  rejectEvidence: (id: string, reason: string) => Promise<void>;
}

export const useEvidenceChain = (evidenceId: string): UseEvidenceChainReturn => {
  const [evidence, setEvidence] = useState<Evidence | null>(null);
  const [chain, setChain] = useState<CustodyRecord[]>([]);
  const [stats, setStats] = useState<EvidenceStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchEvidence = useCallback(async (id: string) => {
    if (!id) {
      setEvidence(null);
      setChain([]);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const [evidenceRes, chainRes, statsRes] = await Promise.all([
        evidenceApi.getEvidenceById(id),
        evidenceApi.getCustodyHistory(id),
        evidenceApi.getEvidenceStats(),
      ]);

      setEvidence(evidenceRes.data || null);
      setChain(chainRes.data || []);
      setStats(statsRes.data || null);
    } catch (err: any) {
      console.error('Error fetching evidence chain:', err);
      setError(err.message || 'Failed to fetch evidence chain');
      setEvidence(null);
      setChain([]);
    } finally {
      setLoading(false);
    }
  }, []);

  const verifyEvidence = useCallback(async (id: string) => {
    try {
      await evidenceApi.verifyEvidence(id);
      await fetchEvidence(id);
    } catch (err) {
      console.error('Error verifying evidence:', err);
      throw err;
    }
  }, [fetchEvidence]);

  const rejectEvidence = useCallback(async (id: string, reason: string) => {
    try {
      await evidenceApi.rejectEvidence(id, reason);
      await fetchEvidence(id);
    } catch (err) {
      console.error('Error rejecting evidence:', err);
      throw err;
    }
  }, [fetchEvidence]);

  useEffect(() => {
    if (evidenceId) {
      fetchEvidence(evidenceId);
    }
  }, [evidenceId, fetchEvidence]);

  return {
    evidence,
    chain,
    stats,
    loading,
    error,
    fetchEvidence,
    verifyEvidence,
    rejectEvidence,
  };
};

export default useEvidenceChain;
