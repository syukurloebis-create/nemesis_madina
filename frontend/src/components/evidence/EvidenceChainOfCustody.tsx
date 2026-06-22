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

  // Loading state
  if (loading) {
    return (
      <div className="flex justify-center items-center h-32">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Error state lainnya
  if (error) {
    return (
      <div className="bg-red-500/10 border border-red-500/30 p-4 rounded-xl text-red-400">
        <AlertTriangle className="w-5 h-5 inline mr-2" />
        {error}
      </div>
    );
  }

  // No evidence
  if (!evidence) {
    return (
      <div className="text-center text-gray-400 py-8">
        <Shield className="w-12 h-12 mx-auto mb-3 opacity-50" />
        <p>Evidence tidak ditemukan</p>
      </div>
    );
  }

  // Render evidence detail
  return (
    <div className={`space-y-4 ${className}`}>
      <div className="glass-card p-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-white font-medium">{evidence.title || 'Evidence'}</h3>
            <p className="text-sm text-gray-400">Status: {evidence.status || 'Unknown'}</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => verifyEvidence(evidence.id)}
              className="px-3 py-1 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700"
            >
              Verify
            </button>
            <button
              onClick={() => setShowRejectModal(true)}
              className="px-3 py-1 bg-red-600 text-white text-sm rounded-lg hover:bg-red-700"
            >
              Reject
            </button>
          </div>
        </div>
        
        <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
          <div className="bg-dark-bg rounded-lg p-2 text-center">
            <p className="text-gray-400">Trust Score</p>
            <p className="text-white font-bold">{evidence.trustScore || 0}%</p>
          </div>
          <div className="bg-dark-bg rounded-lg p-2 text-center">
            <p className="text-gray-400">Confidence</p>
            <p className="text-white font-bold">{evidence.confidence || 0}%</p>
          </div>
          <div className="bg-dark-bg rounded-lg p-2 text-center">
            <p className="text-gray-400">File Type</p>
            <p className="text-white font-bold">{evidence.fileType || 'N/A'}</p>
          </div>
          <div className="bg-dark-bg rounded-lg p-2 text-center">
            <p className="text-gray-400">Created</p>
            <p className="text-white font-bold text-xs">
              {new Date(evidence.createdAt).toLocaleDateString('id-ID')}
            </p>
          </div>
        </div>
      </div>

      {/* Timeline */}
      {chain && chain.length > 0 && (
        <div className="glass-card p-4">
          <h4 className="text-sm font-medium text-gray-400 mb-3">Chain of Custody</h4>
          <EvidenceTimeline events={chain} />
        </div>
      )}

      {/* Stats */}
      {stats && (
        <div className="glass-card p-4">
          <h4 className="text-sm font-medium text-gray-400 mb-3">Statistics</h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
            <div className="bg-dark-bg rounded-lg p-2 text-center">
              <p className="text-gray-400">Total</p>
              <p className="text-white font-bold">{stats.total || 0}</p>
            </div>
            <div className="bg-dark-bg rounded-lg p-2 text-center">
              <p className="text-gray-400">Verified</p>
              <p className="text-green-400 font-bold">{stats.verified || 0}</p>
            </div>
            <div className="bg-dark-bg rounded-lg p-2 text-center">
              <p className="text-gray-400">Pending</p>
              <p className="text-yellow-400 font-bold">{stats.pending || 0}</p>
            </div>
            <div className="bg-dark-bg rounded-lg p-2 text-center">
              <p className="text-gray-400">Rejected</p>
              <p className="text-red-400 font-bold">{stats.rejected || 0}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default EvidenceChainOfCustody;
