// AIRiskScore.tsx - AI Risk Score Card
import React from 'react';
import { TrendingUp, TrendingDown, AlertTriangle } from 'lucide-react';

interface AIRiskScoreProps {
  riskScore: number;
  trend?: number;
  level?: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
}

export const AIRiskScore: React.FC<AIRiskScoreProps> = ({ 
  riskScore = 0, 
  trend = 0,
  level = 'CRITICAL'
}) => {
  const getLevelColor = (score: number) => {
    if (score >= 80) return { color: 'text-red-500', bg: 'bg-red-500/20', border: 'border-red-500/30' };
    if (score >= 60) return { color: 'text-orange-500', bg: 'bg-orange-500/20', border: 'border-orange-500/30' };
    if (score >= 40) return { color: 'text-yellow-500', bg: 'bg-yellow-500/20', border: 'border-yellow-500/30' };
    return { color: 'text-green-500', bg: 'bg-green-500/20', border: 'border-green-500/30' };
  };

  const getLevelLabel = (score: number) => {
    if (score >= 80) return 'CRITICAL';
    if (score >= 60) return 'HIGH';
    if (score >= 40) return 'MEDIUM';
    return 'LOW';
  };

  const colors = getLevelColor(riskScore);
  const levelLabel = getLevelLabel(riskScore);

  return (
    <div className={`bg-dark-card rounded-lg border ${colors.border} p-4 h-full`}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs text-gray-400 font-medium">AI RISK SCORE</span>
        {trend !== 0 && (
          <div className={`flex items-center gap-1 text-xs ${trend > 0 ? 'text-red-400' : 'text-green-400'}`}>
            {trend > 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
            {Math.abs(trend)}%
          </div>
        )}
      </div>
      
      <div className="flex items-end gap-3">
        <span className={`text-4xl font-bold ${colors.color}`}>
          {riskScore}
        </span>
        <span className="text-sm text-gray-500 mb-1">/ 100</span>
      </div>
      
      <div className="flex items-center gap-2 mt-2">
        <AlertTriangle className={`w-4 h-4 ${colors.color}`} />
        <span className={`text-sm font-semibold ${colors.color}`}>
          {levelLabel}
        </span>
      </div>

      {/* Progress Bar */}
      <div className="w-full h-1.5 bg-gray-800 rounded-full mt-3 overflow-hidden">
        <div 
          className={`h-full rounded-full ${riskScore >= 80 ? 'bg-red-500' : riskScore >= 60 ? 'bg-orange-500' : riskScore >= 40 ? 'bg-yellow-500' : 'bg-green-500'}`}
          style={{ width: `${Math.min(riskScore, 100)}%` }}
        />
      </div>
    </div>
  );
};

export default AIRiskScore;
