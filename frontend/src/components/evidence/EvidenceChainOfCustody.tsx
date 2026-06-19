// EvidenceChainOfCustody.tsx - With 404 handling
import React, { useState } from 'react';
import { Shield, AlertTriangle, RefreshCw } from 'lucide-react';
import { useEvidenceChain } from '../../hooks/useEvidenceChain';
import EvidenceTimeline from './EvidenceTimeline';

interface EvidenceChainOfCustodyProps {
  evidenceId: string;
  className?: string;
}

export const EvidenceChainOfCustody: React.FC<EvidenceChainOfCustodyProps> = ({
  evidenceId,
  className = ''
}) => {
  const { evidence, chain, stats, loading, error, verifyEvidence, rejectEvidence, fetchEvidence } = useEvidenceChain(evidenceId);
  const [rejectReason, setRejectReason] = useState('');
  const [showRejectModal, setShowRejectModal] = useState(false);

  // Handle 404 - evidence not found
  if (error && error.includes('404')) {
    return (
      <div className="glass-card p-4 text-center">
        <Shield className="w-12 h-12 text-gray-600 mx-auto mb-3" />
        <p className="text-gray-400">Evidence tidak ditemukan</p>
        <p className="text-xs text-gray-500 mt-1">ID: {evidenceId}</p>
        <button 
          onClick={() => fetchEvidence(evidenceId)}
          className="mt-3 px-4 py-2 bg-primary-500/20 hover:bg-primary-500/30 rounded-lg text-primary-400 text-sm transition-colors"
        >
          <RefreshCw className="w-4 h-4 inline mr-1" />
          Retry
        </button>
      </div>
    );
  }

  // ... rest of component
};
