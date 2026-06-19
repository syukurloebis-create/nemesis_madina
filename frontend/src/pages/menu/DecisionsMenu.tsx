// DecisionsMenu.tsx - ONLY Decisions
import React from 'react';
import DecisionSupport from '../../components/decision/DecisionSupport';

interface DecisionsMenuProps {
  caseId: string;
}

export const DecisionsMenu: React.FC<DecisionsMenuProps> = ({ caseId }) => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white">⚖️ Decision Support</h2>
        <span className="text-sm text-dark-muted">APIP Recommendations</span>
      </div>
      <DecisionSupport caseId={caseId} />
    </div>
  );
};

export default DecisionsMenu;
