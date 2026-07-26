import React from 'react';
import { BaseModal } from './BaseModal';
import { FileText, Calendar, User, AlertTriangle } from 'lucide-react';

interface CaseListModalProps {
  isOpen: boolean;
  onClose: () => void;
  cases: any[];
  title?: string;
}

export const CaseListModal: React.FC<CaseListModalProps> = ({
  isOpen,
  onClose,
  cases,
  title = 'Daftar Kasus',
}) => {
  // Pastikan cases adalah array
  const casesArray = Array.isArray(cases) ? cases : [];
  
  const getStatusBadge = (status: string) => {
    const colors: Record<string, string> = {
      OPEN: 'bg-green-500/20 text-green-400 border-green-500/30',
      INVESTIGATING: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
      CLOSED: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
      PENDING: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    };
    return colors[status] || 'bg-gray-500/20 text-gray-400 border-gray-500/30';
  };

  const getPriorityBadge = (priority: string) => {
    const colors: Record<string, string> = {
      CRITICAL: 'bg-red-500/20 text-red-400 border-red-500/30',
      HIGH: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
      MEDIUM: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
      LOW: 'bg-green-500/20 text-green-400 border-green-500/30',
    };
    return colors[priority] || 'bg-gray-500/20 text-gray-400 border-gray-500/30';
  };

  return (
    <BaseModal isOpen={isOpen} onClose={onClose} title={title} size="xl">
      {casesArray.length === 0 ? (
        <div className="text-center py-8 text-dark-muted">
          <FileText className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p>Belum ada kasus</p>
          <p className="text-sm mt-2">Kasus akan muncul ketika data tersedia</p>
        </div>
      ) : (
        <div className="space-y-3">
          {casesArray.map((caseItem: any, index: number) => (
            <div key={index} className="bg-dark-bg border border-dark-border rounded-lg p-4 hover:border-primary-500/30 transition-all">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`px-2 py-0.5 rounded text-xs font-medium border ${getStatusBadge(caseItem.status)}`}>
                      {caseItem.status || 'OPEN'}
                    </span>
                    <span className={`px-2 py-0.5 rounded text-xs font-medium border ${getPriorityBadge(caseItem.priority)}`}>
                      {caseItem.priority || 'MEDIUM'}
                    </span>
                  </div>
                  <h4 className="text-white font-medium">{caseItem.title || `Kasus #${index + 1}`}</h4>
                  <p className="text-dark-muted text-sm mt-1 line-clamp-2">{caseItem.description || '-'}</p>
                  <div className="flex items-center gap-4 mt-2 text-xs text-dark-muted">
                    <span className="flex items-center gap-1">
                      <User className="w-3 h-3" />
                      {caseItem.assigned_to || 'Unassigned'}
                    </span>
                    <span className="flex items-center gap-1">
                      <Calendar className="w-3 h-3" />
                      {caseItem.created_at ? new Date(caseItem.created_at).toLocaleDateString() : '-'}
                    </span>
                    <span className="flex items-center gap-1">
                      <AlertTriangle className="w-3 h-3" />
                      Risk: {caseItem.risk_score || 0}%
                    </span>
                  </div>
                </div>
                <button className="px-3 py-1.5 text-xs bg-primary-500/10 text-primary-400 border border-primary-500/20 rounded hover:bg-primary-500/20 transition-colors">
                  Detail
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
      <div className="mt-4 pt-4 border-t border-dark-border text-xs text-dark-muted">
        Total: {casesArray.length} kasus
      </div>
    </BaseModal>
  );
};

export default CaseListModal;
