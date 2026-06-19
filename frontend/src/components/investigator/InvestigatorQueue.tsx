// InvestigatorQueue.tsx - Case Queue with Working Buttons
import React from 'react';
import { Briefcase, Clock, AlertTriangle, ChevronRight, Circle } from 'lucide-react';

interface Case {
  id: string;
  title: string;
  status: string;
  risk_score?: number;
  created_at?: string;
  priority?: string;
}

interface InvestigatorQueueProps {
  cases?: Case[];
  recommendations?: any[];
  onCaseClick?: (caseId: string) => void;
  onOpenCase?: (caseId: string) => void;
}

const getStatusBadge = (status: string) => {
  const statusMap: Record<string, { label: string; color: string; bg: string }> = {
    'OPEN': { label: 'OPEN', color: 'text-green-400', bg: 'bg-green-500/20 border-green-500/30' },
    'INVESTIGATING': { label: 'INVESTIGATING', color: 'text-yellow-400', bg: 'bg-yellow-500/20 border-yellow-500/30' },
    'REVIEW': { label: 'REVIEW', color: 'text-orange-400', bg: 'bg-orange-500/20 border-orange-500/30' },
    'CLOSED': { label: 'CLOSED', color: 'text-gray-400', bg: 'bg-gray-500/20 border-gray-500/30' },
    'SCREENING': { label: 'SCREENING', color: 'text-blue-400', bg: 'bg-blue-500/20 border-blue-500/30' },
  };
  return statusMap[status] || statusMap['OPEN'];
};

const getRiskColor = (score: number) => {
  if (score >= 80) return 'text-red-400';
  if (score >= 60) return 'text-orange-400';
  if (score >= 40) return 'text-yellow-400';
  return 'text-green-400';
};

const getRiskBarColor = (score: number) => {
  if (score >= 80) return 'bg-red-500';
  if (score >= 60) return 'bg-orange-500';
  if (score >= 40) return 'bg-yellow-500';
  return 'bg-green-500';
};

export const InvestigatorQueue: React.FC<InvestigatorQueueProps> = ({ 
  cases = [], 
  onCaseClick,
  onOpenCase
}) => {
  const caseList = Array.isArray(cases) ? cases : [];

  const handleClick = (caseId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (onCaseClick) {
      onCaseClick(caseId);
    }
  };

  const handleOpen = (caseId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (onOpenCase) {
      onOpenCase(caseId);
    }
  };

  const totalCases = caseList.length;
  const activeCases = caseList.filter(c => c.status !== 'CLOSED').length;

  return (
    <div className="glass-card p-4">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Briefcase className="w-5 h-5 text-primary-400" />
          <h3 className="text-sm font-semibold text-white">INVESTIGATOR QUEUE</h3>
        </div>
        <div className="flex items-center gap-3 text-xs">
          <span className="text-dark-muted">{totalCases} total cases</span>
          <span className="text-green-400">{activeCases} active</span>
        </div>
      </div>

      <div className="space-y-2 max-h-[400px] overflow-y-auto dark-scrollbar">
        {caseList.length === 0 ? (
          <div className="text-center py-8 text-dark-muted">
            <p>Tidak ada kasus</p>
          </div>
        ) : (
          caseList.map((item) => {
            const statusBadge = getStatusBadge(item.status);
            const riskScore = item.risk_score || 0;
            
            return (
              <div 
                key={item.id} 
                className="bg-dark-bg/50 rounded-lg p-3 border border-dark-border hover:border-primary-500/30 transition-all cursor-pointer group"
                onClick={() => handleClick(item.id, {} as React.MouseEvent)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-xs font-mono text-dark-muted">{item.id}</span>
                      <span className={`text-xs px-2 py-0.5 rounded-full border ${statusBadge.bg} ${statusBadge.color}`}>
                        {statusBadge.label}
                      </span>
                      {item.priority && (
                        <span className={`text-xs px-2 py-0.5 rounded-full ${
                          item.priority === 'HIGH' ? 'bg-red-500/20 text-red-400' :
                          item.priority === 'MEDIUM' ? 'bg-yellow-500/20 text-yellow-400' :
                          'bg-blue-500/20 text-blue-400'
                        }`}>
                          {item.priority}
                        </span>
                      )}
                    </div>

                    <p className="text-sm text-white mt-1 truncate">{item.title || 'Untitled Case'}</p>

                    <div className="flex items-center gap-3 mt-1.5">
                      <div className="flex items-center gap-1.5">
                        <AlertTriangle className="w-3.5 h-3.5 text-dark-muted" />
                        <span className="text-xs text-dark-muted">Risk:</span>
                        <span className={`text-xs font-bold ${getRiskColor(riskScore)}`}>
                          {riskScore}%
                        </span>
                      </div>
                      <div className="w-20 h-1.5 bg-gray-700 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full ${getRiskBarColor(riskScore)}`}
                          style={{ width: `${Math.min(riskScore, 100)}%` }}
                        />
                      </div>
                      {item.created_at && (
                        <div className="flex items-center gap-1.5 ml-auto">
                          <Clock className="w-3 h-3 text-dark-muted" />
                          <span className="text-xs text-dark-muted">
                            {new Date(item.created_at).toLocaleDateString('id-ID')}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center gap-2 ml-3">
                    <button
                      onClick={(e) => handleOpen(item.id, e)}
                      className="px-3 py-1 text-xs bg-primary-500/10 hover:bg-primary-500/20 rounded-lg text-primary-400 transition-colors border border-primary-500/20"
                    >
                      Open
                    </button>
                    <button
                      onClick={(e) => handleClick(item.id, e)}
                      className="p-1.5 text-dark-muted hover:text-primary-400 transition-colors rounded-lg hover:bg-dark-bg"
                      title="View details"
                    >
                      <ChevronRight className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>

      <div className="mt-3 pt-3 border-t border-dark-border flex justify-between text-xs text-dark-muted">
        <span>Total: {totalCases} cases</span>
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-green-400" />
            Open
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-yellow-400" />
            Investigating
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-red-400" />
            Closed
          </span>
        </div>
      </div>
    </div>
  );
};

export default InvestigatorQueue;
