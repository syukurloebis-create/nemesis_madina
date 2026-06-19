import React, { useEffect, useState } from 'react';
import { useAuthStore } from '../../stores/authStore';
import { api } from '../../services/api';

interface HashChainVerificationProps {
  caseId: string;
}

interface VerificationResult {
  case_id: string;
  total_events: number;
  chain_valid: boolean;
  broken_at_version: number | null;
  verified_at: string;
}

const HashChainVerification: React.FC<HashChainVerificationProps> = ({ caseId }) => {
  const [verification, setVerification] = useState<VerificationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { token } = useAuthStore();

  const verifyChain = async () => {
    if (!caseId || !token) return;
    
    setLoading(true);
    setError(null);
    try {
      const result = await api.verifyHashChain(caseId);
      setVerification(result);
    } catch (error) {
      console.error('Verification failed:', error);
      setError('Gagal memverifikasi rantai hash');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (caseId) {
      verifyChain();
    }
  }, [caseId]);

  if (loading) {
    return (
      <div className="text-center py-4 text-gray-400">
        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-green-500 mx-auto mb-2"></div>
        Memverifikasi rantai hash...
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-4 text-red-400">
        <p>{error}</p>
        <button onClick={verifyChain} className="mt-2 text-sm text-blue-400 hover:text-blue-300">
          Coba Lagi
        </button>
      </div>
    );
  }

  if (!verification) {
    return (
      <div className="text-center py-8 text-gray-500">
        <p>Klik "Lihat Forensik" pada kasus untuk verifikasi rantai hash</p>
      </div>
    );
  }

  return (
    <div className={`p-4 rounded-lg ${verification.chain_valid ? 'bg-green-500/10 border border-green-500/30' : 'bg-red-500/10 border border-red-500/30'}`}>
      <div className="flex items-center gap-3 mb-3">
        <div className={`w-12 h-12 rounded-full flex items-center justify-center ${verification.chain_valid ? 'bg-green-500/20' : 'bg-red-500/20'}`}>
          <span className="text-2xl">{verification.chain_valid ? '✅' : '❌'}</span>
        </div>
        <div>
          <h4 className={`font-semibold text-lg ${verification.chain_valid ? 'text-green-400' : 'text-red-400'}`}>
            {verification.chain_valid ? 'Rantai Valid' : 'Rantai Rusak'}
          </h4>
          <p className="text-xs text-gray-400">
            {verification.total_events} kejadian diverifikasi
            {verification.broken_at_version && ` | Rusak pada versi ${verification.broken_at_version}`}
          </p>
        </div>
      </div>
      
      <div className="mt-3 pt-3 border-t border-gray-700">
        <div className="flex items-center justify-between text-xs">
          <span className="text-gray-400">Diverifikasi pada:</span>
          <span className="text-gray-300">{new Date(verification.verified_at).toLocaleString()}</span>
        </div>
        <div className="flex items-center justify-between text-xs mt-1">
          <span className="text-gray-400">Rantai Kriptografis:</span>
          <span className={verification.chain_valid ? 'text-green-400 font-semibold' : 'text-red-400 font-semibold'}>
            {verification.chain_valid ? 'TERVERIFIKASI' : 'TERPUTUS'}
          </span>
        </div>
      </div>
    </div>
  );
};

export default HashChainVerification;
