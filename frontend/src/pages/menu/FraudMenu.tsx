// FraudMenu.tsx - ONLY Fraud
import React from 'react';
import { FraudPatternDetection } from '../../components/fraud/FraudPatternDetection';

interface FraudMenuProps {
  onInvestigate?: (id: string) => void;
}

export const FraudMenu: React.FC<FraudMenuProps> = ({ onInvestigate }) => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white">🚨 Fraud Detection Center</h2>
        <span className="text-xs text-red-400 animate-pulse">● LIVE</span>
      </div>
      <FraudPatternDetection onInvestigate={onInvestigate} />
    </div>
  );
};

export default FraudMenu;
