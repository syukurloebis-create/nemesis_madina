// CasesMenu.tsx - Cases Management with New Case Form
import React, { useState } from 'react';
import { useDashboardData } from '../../hooks/useDashboardData';
import { InvestigatorQueue } from '../../components/investigator/InvestigatorQueue';
import CaseDetail from '../../components/cases/CaseDetail';
import { X, Plus } from 'lucide-react';

interface CasesMenuProps {
  caseId: string;
}

export const CasesMenu: React.FC<CasesMenuProps> = ({ caseId }) => {
  const { loading, error, data } = useDashboardData(caseId);
  const [selectedCaseId, setSelectedCaseId] = useState<string | null>(null);
  const [showNewCase, setShowNewCase] = useState(false);
  const [newCaseTitle, setNewCaseTitle] = useState('');
  const [newCaseDescription, setNewCaseDescription] = useState('');

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-6 text-center">
        <p className="text-red-400 font-semibold">Error: {error}</p>
      </div>
    );
  }

  const { cases } = data;

  const handleCaseClick = (id: string) => {
    console.log('📋 Detail case:', id);
    setSelectedCaseId(id);
  };

  const handleOpenCase = (id: string) => {
    console.log('🔓 Opening case for investigation:', id);
    setSelectedCaseId(id);
    // TODO: Update case status to INVESTIGATING
  };

  const handleNewCase = () => {
    setShowNewCase(true);
  };

  const handleCreateCase = () => {
    console.log('📝 Creating case:', newCaseTitle);
    // TODO: API call to create case
    alert(`Case "${newCaseTitle}" created!`);
    setShowNewCase(false);
    setNewCaseTitle('');
    setNewCaseDescription('');
  };

  const handleCloseDetail = () => {
    setSelectedCaseId(null);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">📋 Cases Management</h2>
          <p className="text-sm text-dark-muted mt-1">Kelola dan pantau kasus investigasi</p>
        </div>
        <button 
          onClick={handleNewCase}
          className="px-4 py-2 bg-primary-500/20 hover:bg-primary-500/30 rounded-lg text-sm text-primary-400 transition-colors border border-primary-500/20 flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          New Case
        </button>
      </div>

      <InvestigatorQueue 
        cases={cases} 
        onCaseClick={handleCaseClick}
        onOpenCase={handleOpenCase}
      />

      {/* Case Detail Modal */}
      {selectedCaseId && (
        <CaseDetail 
          caseId={selectedCaseId} 
          onClose={handleCloseDetail}
        />
      )}

      {/* New Case Modal */}
      {showNewCase && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 animate-fade-in">
          <div className="glass-card w-full max-w-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Plus className="w-5 h-5 text-primary-400" />
                <h3 className="text-lg font-bold text-white">New Case</h3>
              </div>
              <button 
                onClick={() => setShowNewCase(false)}
                className="p-1 text-dark-muted hover:text-white transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="text-xs text-dark-muted block mb-1">Title *</label>
                <input
                  type="text"
                  value={newCaseTitle}
                  onChange={(e) => setNewCaseTitle(e.target.value)}
                  placeholder="Enter case title..."
                  className="w-full bg-dark-bg/50 border border-dark-border rounded-lg px-3 py-2 text-sm text-white placeholder-dark-muted focus:outline-none focus:border-primary-500/50"
                />
              </div>
              <div>
                <label className="text-xs text-dark-muted block mb-1">Description</label>
                <textarea
                  value={newCaseDescription}
                  onChange={(e) => setNewCaseDescription(e.target.value)}
                  placeholder="Enter case description..."
                  rows={3}
                  className="w-full bg-dark-bg/50 border border-dark-border rounded-lg px-3 py-2 text-sm text-white placeholder-dark-muted focus:outline-none focus:border-primary-500/50 resize-none"
                />
              </div>
              <div className="flex gap-2 pt-2">
                <button
                  onClick={handleCreateCase}
                  disabled={!newCaseTitle.trim()}
                  className="flex-1 px-4 py-2 bg-primary-500 hover:bg-primary-600 rounded-lg text-sm text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Create Case
                </button>
                <button
                  onClick={() => setShowNewCase(false)}
                  className="px-4 py-2 bg-dark-bg/50 border border-dark-border rounded-lg text-sm text-dark-muted hover:text-white transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CasesMenu;
