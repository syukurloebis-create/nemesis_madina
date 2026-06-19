// hooks/useEvidenceChain.ts - Custom hook for evidence chain
import { useState, useEffect, useCallback } from 'react';
import { Evidence, EvidenceChain, EvidenceStats } from '../types/evidence';
import evidenceApi from '../services/evidenceApi';

interface UseEvidenceChainReturn {
  evidence: Evidence | null;
  chain: EvidenceChain | null;
  stats: EvidenceStats | null;
  loading: boolean;
  error: string | null;
  fetchEvidence: (id: string) => Promise<void>;
  verifyEvidence: (id: string) => Promise<void>;
  rejectEvidence: (id: string, reason?: string) => Promise<void>;
}

export const useEvidenceChain = (evidenceId?: string): UseEvidenceChainReturn => {
  const [evidence, setEvidence] = useState<Evidence | null>(null);
  const [chain, setChain] = useState<EvidenceChain | null>(null);
  const [stats, setStats] = useState<EvidenceStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = useCallback(async () => {
    try {
      const statsData = await evidenceApi.getEvidenceStats();
      setStats(statsData);
    } catch (err) {
      console.error('❌ Error fetching evidence stats:', err);
    }
  }, []);

  const fetchEvidence = useCallback(async (id: string) => {
    try {
      setLoading(true);
      setError(null);
      
      const [evidenceData, chainData] = await Promise.all([
        evidenceApi.getEvidence(id),
        evidenceApi.getEvidenceChain(id)
      ]);
      
      setEvidence(evidenceData);
      setChain(chainData);
      
      // Also fetch stats if not loaded
      if (!stats) {
        await fetchStats();
      }
    } catch (err: any) {
      console.error('❌ Error fetching evidence chain:', err);
      setError(err.response?.data?.detail || 'Gagal memuat data evidence');
    } finally {
      setLoading(false);
    }
  }, [stats, fetchStats]);

  const verifyEvidence = useCallback(async (id: string) => {
    try {
      const updated = await evidenceApi.verifyEvidence(id);
      setEvidence(updated);
      // Refresh chain
      if (id === evidenceId) {
        await fetchEvidence(id);
      }
      await fetchStats();
    } catch (err: any) {
      console.error('❌ Error verifying evidence:', err);
      throw err;
    }
  }, [evidenceId, fetchEvidence, fetchStats]);

  const rejectEvidence = useCallback(async (id: string, reason?: string) => {
    try {
      const updated = await evidenceApi.rejectEvidence(id, reason);
      setEvidence(updated);
      // Refresh chain
      if (id === evidenceId) {
        await fetchEvidence(id);
      }
      await fetchStats();
    } catch (err: any) {
      console.error('❌ Error rejecting evidence:', err);
      throw err;
    }
  }, [evidenceId, fetchEvidence, fetchStats]);

  useEffect(() => {
    fetchStats();
    if (evidenceId) {
      fetchEvidence(evidenceId);
    } else {
      setLoading(false);
    }
  }, [evidenceId, fetchEvidence, fetchStats]);

  return {
    evidence,
    chain,
    stats,
    loading,
    error,
    fetchEvidence,
    verifyEvidence,
    rejectEvidence
  };
};

export default useEvidenceChain;
