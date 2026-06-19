// EvidenceIntelligence.tsx - Evidence Chain & Intelligence
import React from 'react';
import { FileText, ArrowDown, Shield, CheckCircle, Clock, AlertTriangle } from 'lucide-react';

interface EvidenceIntelligenceProps {
  evidence: {
    total?: number;
    verified?: number;
    pending?: number;
    rejected?: number;
  };
}

export const EvidenceIntelligence: React.FC<EvidenceIntelligenceProps> = ({ evidence }) => {
  const { total = 0, verified = 0, pending = 0, rejected = 0 } = evidence || {};
  const trustScore = total > 0 ? Math.round((verified / total) * 100) : 0;

  // Mock evidence chain
  const chain = [
    { step: 'Document', status: 'verified', icon: FileText },
    { step: 'Transaction', status: 'verified', icon: FileText },
    { step: 'Vendor', status: 'pending', icon: Shield },
    { step: 'Decision', status: 'pending', icon: FileText },
    { step: 'Finding', status: 'pending', icon: AlertTriangle },
  ];

  const getStatusColor = (status: string) => {
    switch(status) {
      case 'verified': return 'text-green-400 border-green-400/30 bg-green-500/10';
      case 'pending': return 'text-yellow-400 border-yellow-400/30 bg-yellow-500/10';
      case 'rejected': return 'text-red-400 border-red-400/30 bg-red-500/10';
      default: return 'text-gray-400 border-gray-400/30 bg-gray-500/10';
    }
  };

  const getStatusIcon = (status: string) => {
    switch(status) {
      case 'verified': return <CheckCircle className="w-4 h-4 text-green-400" />;
      case 'pending': return <Clock className="w-4 h-4 text-yellow-400" />;
      case 'rejected': return <AlertTriangle className="w-4 h-4 text-red-400" />;
      default: return <Clock className="w-4 h-4 text-gray-400" />;
    }
  };

  return (
    <div className="bg-dark-card rounded-lg border border-dark-border p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-white">📄 EVIDENCE INTELLIGENCE</h3>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-400">Trust Score</span>
          <span className={`text-sm font-bold ${trustScore >= 70 ? 'text-green-400' : trustScore >= 40 ? 'text-yellow-400' : 'text-red-400'}`}>
            {trustScore}%
          </span>
        </div>
      </div>

      {/* Evidence Stats */}
      <div className="grid grid-cols-4 gap-2 mb-4">
        <div className="bg-dark-bg rounded-lg p-2 text-center">
          <p className="text-lg font-bold text-white">{total}</p>
          <p className="text-xs text-gray-500">Total</p>
        </div>
        <div className="bg-dark-bg rounded-lg p-2 text-center">
          <p className="text-lg font-bold text-green-400">{verified}</p>
          <p className="text-xs text-gray-500">Verified</p>
        </div>
        <div className="bg-dark-bg rounded-lg p-2 text-center">
          <p className="text-lg font-bold text-yellow-400">{pending}</p>
          <p className="text-xs text-gray-500">Pending</p>
        </div>
        <div className="bg-dark-bg rounded-lg p-2 text-center">
          <p className="text-lg font-bold text-red-400">{rejected}</p>
          <p className="text-xs text-gray-500">Rejected</p>
        </div>
      </div>

      {/* Evidence Chain */}
      <div className="space-y-1">
        <p className="text-xs text-gray-500 mb-2">Evidence Chain</p>
        {chain.map((item, idx) => (
          <div key={idx} className="flex items-center gap-3">
            <div className={`p-1.5 rounded-lg border ${getStatusColor(item.status)}`}>
              <item.icon className="w-3 h-3" />
            </div>
            <span className="text-sm text-gray-300 flex-1">{item.step}</span>
            <div className="flex items-center gap-1.5">
              {getStatusIcon(item.status)}
              <span className={`text-xs capitalize ${getStatusColor(item.status).split(' ')[0]}`}>
                {item.status}
              </span>
            </div>
            {idx < chain.length - 1 && (
              <ArrowDown className="w-3 h-3 text-gray-600 absolute ml-6 mt-6" />
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default EvidenceIntelligence;
