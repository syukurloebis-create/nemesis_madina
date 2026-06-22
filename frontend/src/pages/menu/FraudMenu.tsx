// src/pages/menu/FraudMenu.tsx
import React from 'react';
import FraudPatternDetection from '../../components/fraud/FraudPatternDetection';

interface FraudMenuProps {
  onInvestigate?: (patternId: string) => void;
  caseId?: string;
}

export const FraudMenu: React.FC<FraudMenuProps> = ({ 
  onInvestigate, 
  caseId = '446e216d-eb0e-487e-8e6b-ec943468ea20' 
}) => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white">🔍 Fraud Detection Center</h2>
      </div>
      <FraudPatternDetection 
        caseId={caseId}
        onInvestigate={onInvestigate}
      />
    </div>
  );
};

export default FraudMenu;
