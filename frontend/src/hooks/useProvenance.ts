// hooks/useProvenance.ts - Custom hook for provenance data
import { useState, useEffect } from 'react';
import { ProvenanceData, RiskContributor } from '../types/provenance';
import provenanceApi from '../services/provenanceApi';

interface UseProvenanceReturn {
  data: ProvenanceData | null;
  loading: boolean;
  error: string | null;
  riskContributors: RiskContributor[];
  refetch: () => void;
}

export const useProvenance = (caseId: string): UseProvenanceReturn => {
  const [data, setData] = useState<ProvenanceData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [riskContributors, setRiskContributors] = useState<RiskContributor[]>([]);

  const fetchData = async () => {
    if (!caseId) {
      setError('No case ID provided');
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const result = await provenanceApi.getProvenance(caseId);
      setData(result);
      setRiskContributors(result.risk_contributors || []);
    } catch (err: any) {
      console.error('❌ Error fetching provenance:', err);
      setError(err.response?.data?.detail || 'Gagal memuat data risk reasoning');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [caseId]);

  return {
    data,
    loading,
    error,
    riskContributors,
    refetch: fetchData
  };
};

export default useProvenance;
