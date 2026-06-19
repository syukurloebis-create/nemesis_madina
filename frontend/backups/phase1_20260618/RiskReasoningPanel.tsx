// RiskReasoningPanel - Enhanced Explainable AI
import React from 'react';
import { AlertTriangle, Info, ChevronDown, ChevronUp } from 'lucide-react';

interface RiskFactor {
  factor: string;
  contribution: number;
  description: string;
  evidence: string[];
}

export const RiskReasoningPanel: React.FC<{ caseId: string }> = ({ caseId }) => {
  // ... existing code ...
  
  // TAMBAHKAN: Evidence trail untuk setiap faktor
  // TAMBAHKAN: Expandable details
  // TAMBAHKAN: Action buttons (Investigate, Report)
  
  return (
    <div className="bg-dark-card rounded-lg border border-dark-border p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-white">🧠 RISK REASONING</h3>
        <span className="text-xs text-blue-400">Explainable AI</span>
      </div>
      
      {/* Risk Score */}
      <div className="flex items-center gap-4 mb-4">
        <div className="text-3xl font-bold text-red-400">85</div>
        <div className="flex-1">
          <div className="w-full h-2 bg-gray-700 rounded-full overflow-hidden">
            <div className="h-full bg-red-500 rounded-full" style={{ width: '85%' }} />
          </div>
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>HIGH RISK</span>
            <span>Critical</span>
          </div>
        </div>
      </div>
      
      {/* Risk Factors with Evidence Trail */}
      <div className="space-y-3">
        {factors.map((factor, idx) => (
          <div key={idx} className="bg-dark-bg rounded-lg p-3 border border-dark-border">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 text-yellow-400" />
                <span className="text-sm text-white">{factor.factor}</span>
              </div>
              <span className="text-sm font-bold text-yellow-400">{factor.contribution}%</span>
            </div>
            <p className="text-xs text-gray-400 mt-1">{factor.description}</p>
            
            {/* Evidence Trail */}
            <div className="mt-2 pt-2 border-t border-dark-border">
              <p className="text-xs text-gray-500">📄 Evidence:</p>
              <ul className="text-xs text-gray-400 list-disc list-inside mt-1">
                {factor.evidence.map((ev, i) => (
                  <li key={i}>{ev}</li>
                ))}
              </ul>
            </div>
          </div>
        ))}
      </div>
      
      {/* Action Buttons */}
      <div className="flex gap-2 mt-4 pt-3 border-t border-dark-border">
        <button className="flex-1 px-3 py-1.5 bg-red-500/20 hover:bg-red-500/30 rounded-lg text-sm text-red-400 transition-colors">
          🔍 Investigate
        </button>
        <button className="flex-1 px-3 py-1.5 bg-blue-500/20 hover:bg-blue-500/30 rounded-lg text-sm text-blue-400 transition-colors">
          📊 Generate Report
        </button>
      </div>
    </div>
  );
};
