import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import { AlertCircle, CheckCircle, HelpCircle } from 'lucide-react';

interface RiskFactor {
  name: string;
  impact: 'high' | 'medium' | 'low';
  score: number;
  description: string;
}

interface RiskReasoning {
  risk_score: number;
  confidence: number;
  level: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  factors: RiskFactor[];
  timestamp: string;
}

interface RiskReasoningPanelProps {
  caseId?: string;
  onRiskSelect?: (factor: RiskFactor) => void;
}

export const RiskReasoningPanel: React.FC<RiskReasoningPanelProps> = ({
  caseId,
  onRiskSelect,
}) => {
  const [data, setData] = useState<RiskReasoning | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      setError(null);
      try {
        const params = caseId ? { case_id: caseId } : undefined;
        const response = await api.get('/api/v1/risk/reasoning', { params });
        setData(response?.data || response);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load risk reasoning');
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, [caseId]);

  if (loading) {
    return (
      <div className="animate-pulse space-y-4">
        <div className="h-8 bg-gray-700 rounded w-1/3" />
        <div className="h-20 bg-gray-700 rounded" />
        <div className="space-y-2">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-12 bg-gray-700 rounded" />
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 text-red-400">
        <p>Error: {error}</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="bg-gray-800/50 rounded-xl p-6 text-center text-gray-400">
        No risk data available
      </div>
    );
  }

  const levelColors = {
    CRITICAL: 'text-red-400 bg-red-500/10 border-red-500/30',
    HIGH: 'text-orange-400 bg-orange-500/10 border-orange-500/30',
    MEDIUM: 'text-yellow-400 bg-yellow-500/10 border-yellow-500/30',
    LOW: 'text-green-400 bg-green-500/10 border-green-500/30',
  };

  const impactIcons = {
    high: <AlertCircle className="w-4 h-4 text-red-400" />,
    medium: <HelpCircle className="w-4 h-4 text-yellow-400" />,
    low: <CheckCircle className="w-4 h-4 text-green-400" />,
  };

  return (
    <div className="bg-gray-800/50 rounded-xl border border-gray-700 p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">Risk Reasoning</h3>
        <div className="flex items-center gap-3">
          <span className="text-sm text-gray-400">Confidence: {(data.confidence * 100).toFixed(0)}%</span>
          <span className={`px-3 py-1 rounded-full text-xs font-medium ${levelColors[data.level]}`}>
            {data.level}
          </span>
        </div>
      </div>

      {/* Score */}
      <div className="flex items-center gap-4 mb-6">
        <div className="text-4xl font-bold text-white">{data.risk_score}</div>
        <div className="text-sm text-gray-400">Risk Score</div>
      </div>

      {/* Factors */}
      <div className="space-y-3">
        <h4 className="text-sm font-medium text-gray-400">Contributing Factors</h4>
        {data.factors.map((factor, index) => (
          <div
            key={index}
            className="flex items-center justify-between p-3 bg-gray-900/50 rounded-lg hover:bg-gray-900/70 transition-colors cursor-pointer"
            onClick={() => onRiskSelect?.(factor)}
          >
            <div className="flex items-center gap-3">
              {impactIcons[factor.impact]}
              <div>
                <p className="text-white text-sm font-medium">{factor.name}</p>
                <p className="text-xs text-gray-400">{factor.description}</p>
              </div>
            </div>
            <div className="text-sm font-medium text-white">{factor.score}%</div>
          </div>
        ))}
      </div>

      {/* Timestamp */}
      <div className="mt-4 text-xs text-gray-500">
        Last updated: {new Date(data.timestamp).toLocaleString()}
      </div>
    </div>
  );
};

export default RiskReasoningPanel;
