// src/components/intelligence/IntelligenceKPICards.tsx
import React from 'react';

interface IntelligenceComponents {
  case_risk: number;
  graph_risk: number;
  fraud_score: number;
  evidence_trust: number;
}

interface IntelligenceKPICardsProps {
  riskScore: number;
  normalizedRisk: 'HIGH' | 'MEDIUM' | 'LOW' | 'CRITICAL';
  components: IntelligenceComponents;
  className?: string;
}

const normalizedRiskColors = {
  CRITICAL: { 
    bg: 'bg-red-500/20', 
    border: 'border-red-500/50', 
    text: 'text-red-400', 
    badge: 'bg-red-500/30 text-red-300' 
  },
  HIGH: { 
    bg: 'bg-orange-500/20', 
    border: 'border-orange-500/50', 
    text: 'text-orange-400', 
    badge: 'bg-orange-500/30 text-orange-300' 
  },
  MEDIUM: { 
    bg: 'bg-yellow-500/20', 
    border: 'border-yellow-500/50', 
    text: 'text-yellow-400', 
    badge: 'bg-yellow-500/30 text-yellow-300' 
  },
  LOW: { 
    bg: 'bg-green-500/20', 
    border: 'border-green-500/50', 
    text: 'text-green-400', 
    badge: 'bg-green-500/30 text-green-300' 
  },
};

const IntelligenceKPICards: React.FC<IntelligenceKPICardsProps> = ({
  riskScore,
  normalizedRisk,
  components,
  className = '',
}) => {
  const normalizedRisk =
    normalizedRisk.toUpperCase() as keyof typeof normalizedRiskColors;

  const colors =
    normalizedRiskColors[normalizedRisk]
    || normalizedRiskColors.LOW;

  const kpiItems = [
    { label: 'Risiko Kasus', value: components.case_risk, color: 'text-red-400', bg: 'bg-red-500/10' },
    { label: 'Risiko Graf', value: components.graph_risk, color: 'text-purple-400', bg: 'bg-purple-500/10' },
    { label: 'Skor Fraud', value: components.fraud_score, color: 'text-orange-400', bg: 'bg-orange-500/10' },
    { label: 'Kepercayaan Bukti', value: components.evidence_trust, color: 'text-blue-400', bg: 'bg-blue-500/10' },
  ];

  return (
    <div className={`bg-dark-card rounded-xl shadow-lg border ${colors.border} p-6 ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">🧠 Skor Kecerdasan</h3>
        <span className={`px-3 py-1 rounded-full text-sm font-medium ${colors.badge}`}>
          {normalizedRisk}
        </span>
      </div>

      <div className="flex items-center gap-6 mb-6">
        <div className={`text-5xl font-bold ${colors.text}`}>
          {riskScore.toFixed(0)}
        </div>
        <div className="text-sm text-gray-400">/ 100</div>
        <div className="flex-1">
          <div className="w-full bg-gray-700 rounded-full h-3">
            <div
              className={`h-3 rounded-full transition-all duration-700 ${
                normalizedRisk === 'CRITICAL' ? 'bg-red-500' :
                normalizedRisk === 'HIGH' ? 'bg-orange-500' :
                normalizedRisk === 'MEDIUM' ? 'bg-yellow-500' : 'bg-green-500'
              }`}
              style={{ width: `${Math.min(riskScore, 100)}%` }}
            />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {kpiItems.map((item) => (
          <div key={item.label} className={`${item.bg} rounded-lg p-3 text-center`}>
            <p className={`text-xl font-bold ${item.color}`}>
              {item.value.toFixed(1)}
            </p>
            <p className="text-xs text-gray-400">{item.label}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default IntelligenceKPICards;
