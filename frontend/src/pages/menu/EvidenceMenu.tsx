// EvidenceMenu.tsx - Evidence Management
import React, { useState } from 'react';
import { EvidenceChainOfCustody } from '../../components/evidence/EvidenceChainOfCustody';
import EvidenceUpload from '../../components/evidence/EvidenceUpload';
import { useEvidenceChain } from '../../hooks/useEvidenceChain';

interface EvidenceMenuProps {
  evidenceId: string;
  caseId?: string;
}

export const EvidenceMenu: React.FC<EvidenceMenuProps> = ({ 
  evidenceId,
  caseId = '446e216d-eb0e-487e-8e6b-ec943468ea20'
}) => {
  const [refreshKey, setRefreshKey] = useState(0);
  const { stats } = useEvidenceChain(evidenceId);

  const handleUploadComplete = () => {
    setRefreshKey(prev => prev + 1);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white">🔗 Evidence Management</h2>
        <div className="flex items-center gap-4 text-sm">
          <span className="text-dark-muted">Total: {stats?.total || 0}</span>
          <span className="text-green-400">Verified: {stats?.verified || 0}</span>
          <span className="text-yellow-400">Pending: {stats?.pending || 0}</span>
          <span className="text-red-400">Rejected: {stats?.rejected || 0}</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <EvidenceUpload 
            caseId={caseId} 
            onUploadComplete={handleUploadComplete}
          />
        </div>
        <div className="lg:col-span-2">
          <EvidenceChainOfCustody 
            key={refreshKey}
            evidenceId={evidenceId} 
          />
        </div>
      </div>
    </div>
  );
};

export default EvidenceMenu;
