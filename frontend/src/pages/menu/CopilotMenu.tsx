// CopilotMenu.tsx - AI Copilot
import React from 'react';
import { AICopilot } from '../../components/copilot/AICopilot';

export const CopilotMenu: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white">🤖 AI Copilot Assistant</h2>
        <span className="text-xs text-green-400 animate-pulse">● ONLINE</span>
      </div>

      <AICopilot />
    </div>
  );
};

export default CopilotMenu;
