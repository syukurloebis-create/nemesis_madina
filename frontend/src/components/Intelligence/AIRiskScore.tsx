// src/components/intelligence/AIRiskScore.tsx - AI Risk Score (FIXED)
import React from 'react';

interface AIRiskScoreProps {
  score: number;
  level: string;
  caseId: string;
  className?: string;
}

const riskLevelColors = {
  CRITICAL: {
    bg: 'bg-red-600/20',
    border: 'border-red-500/50',
    text: 'text-red-400',
    badge: 'bg-red-600/30 text-red-300'
  },
  HIGH: {
    bg: 'bg-orange-600/20',
    border: 'border-orange-500/50',
    text: 'text-orange-400',
    badge: 'bg-orange-600/30 text-orange-300'
  },
  MEDIUM: {
    bg: 'bg-yellow-600/20',
    border: 'border-yellow-500/50',
    text: 'text-yellow-400',
    badge: 'bg-yellow-600/30 text-yellow-300'
  },
  LOW: {
    bg: 'bg-green-600/20',
    border: 'border-green-500/50',
    text: 'text-green-400',
    badge: 'bg-green-600/30 text-green-300'
  }
};

export const AIRiskScore: React.FC<AIRiskScoreProps> = ({
  score,
  level,
  caseId,
  className = ''
}) => {
  const colors = riskLevelColors[level as keyof typeof riskLevelColors] || riskLevelColors.LOW;

  // ============ FIX: Display real score ============
  return (
    <div className={`bg-dark-card rounded-xl shadow-lg border ${colors.border} p-6 ${className}`}>
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-white">🎯 Skor Risiko AI</h3>
          <p className="text-sm text-gray-400">Kasus: {caseId.slice(0, 8)}...</p>
        </div>
        <span className={`px-3 py-1 rounded-full text-sm font-medium ${colors.badge}`}>
          {level}
        </span>
      </div>

      <div className="mt-4 flex items-center gap-6">
        <div className={`text-6xl font-bold ${colors.text}`}>
          {score.toFixed(0)}
        </div>
        <div className="text-sm text-gray-400">/ 100</div>
        <div className="flex-1">
          <div className="w-full bg-gray-700 rounded-full h-4">
            <div
              className={`h-4 rounded-full transition-all duration-700 ${
                level === 'CRITICAL' ? 'bg-red-500' :
                level === 'HIGH' ? 'bg-orange-500' :
                level === 'MEDIUM' ? 'bg-yellow-500' : 'bg-green-500'
              }`}
              style={{ width: `${Math.min(score, 100)}%` }}
            />
          </div>
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>Rendah</span>
            <span>Sedang</span>
            <span>Tinggi</span>
            <span>Kritis</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIRiskScore;
