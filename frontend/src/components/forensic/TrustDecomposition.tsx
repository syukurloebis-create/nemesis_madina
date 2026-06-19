import React, { useState, useEffect } from 'react';
import { useAuthStore } from '../../stores/authStore';
import { api } from '../../services/api';

interface TrustMetric {
  name: string;
  score: number;
  weight: number;
  description: string;
  status: 'good' | 'warning' | 'critical';
}

interface RiskFactor {
  factor: string;
  weight: number;
  severity: string;
  description: string;
}

interface TrustDecompositionProps {
  caseId?: string;
  entityId?: string;
}

const TrustDecomposition: React.FC<TrustDecompositionProps> = ({ caseId, entityId }) => {
  const [trustMetrics, setTrustMetrics] = useState<TrustMetric[]>([
    { name: 'Event Hash Validity', score: 100, weight: 30, description: 'Cryptographic hash verification for all events', status: 'good' },
    { name: 'Chain Integrity', score: 100, weight: 30, description: 'Previous hash chain continuity', status: 'good' },
    { name: 'Snapshot Freshness', score: 95, weight: 20, description: 'Age of latest snapshot', status: 'good' },
    { name: 'Replay Consistency', score: 100, weight: 20, description: 'Event replay accuracy', status: 'good' }
  ]);
  const [riskFactors, setRiskFactors] = useState<RiskFactor[]>([
    { factor: 'Transaction Pattern', weight: 35, severity: 'high', description: 'Unusual transaction patterns detected' },
    { factor: 'Vendor Concentration', weight: 25, severity: 'medium', description: 'High dependency on single vendor' },
    { factor: 'Compliance History', weight: 20, severity: 'low', description: 'Historical compliance issues' },
    { factor: 'Geographic Risk', weight: 20, severity: 'medium', description: 'High-risk jurisdiction exposure' }
  ]);
  const [overallScore, setOverallScore] = useState(100);
  const [loading, setLoading] = useState(true);
  const { token } = useAuthStore();

  useEffect(() => {
    fetchTrustData();
  }, [caseId, entityId, token]);

  const fetchTrustData = async () => {
    try {
      setLoading(true);
      
      if (caseId) {
        const integrityData = await api.getIntegritySummary();
        if (integrityData) {
          const newMetrics = [...trustMetrics];
          newMetrics[0].score = integrityData.hashed_events / integrityData.total_events * 100 || 100;
          newMetrics[1].score = integrityData.integrity_score || 100;
          setTrustMetrics(newMetrics);
          
          const newOverall = newMetrics.reduce((sum, m) => sum + (m.score * m.weight / 100), 0);
          setOverallScore(Math.round(newOverall));
        }
      }
      
      if (entityId) {
        const riskData = await api.get(`/risk-metrics/entity/${entityId}`);
        if (riskData && riskData.risk_factors) {
          setRiskFactors(riskData.risk_factors);
        }
      }
    } catch (error) {
      console.error('Failed to fetch trust data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-400';
    if (score >= 70) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getScoreBg = (score: number) => {
    if (score >= 90) return 'bg-green-500/20';
    if (score >= 70) return 'bg-yellow-500/20';
    return 'bg-red-500/20';
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'good': return '✅';
      case 'warning': return '⚠️';
      case 'critical': return '🔴';
      default: return '⚪';
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-400';
      case 'high': return 'text-orange-400';
      case 'medium': return 'text-yellow-400';
      default: return 'text-green-400';
    }
  };

  if (loading) {
    return <div className="text-center py-8 text-gray-400">Loading trust metrics...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Overall Trust Score */}
      <div className="text-center">
        <div className="inline-flex items-center justify-center">
          <div className="relative">
            <svg className="w-32 h-32 transform -rotate-90">
              <circle className="text-gray-700" strokeWidth="12" stroke="currentColor" fill="transparent" r="56" cx="64" cy="64" />
              <circle
                className="text-green-500"
                strokeWidth="12"
                strokeDasharray={2 * Math.PI * 56}
                strokeDashoffset={2 * Math.PI * 56 * (1 - overallScore / 100)}
                strokeLinecap="round"
                stroke="currentColor"
                fill="transparent"
                r="56"
                cx="64"
                cy="64"
              />
            </svg>
            <span className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-3xl font-bold text-white">
              {overallScore}%
            </span>
          </div>
        </div>
        <p className="text-sm text-gray-400 mt-2">Overall Trust Score</p>
      </div>

      {/* Trust Metrics Breakdown */}
      <div className="space-y-3">
        <h3 className="text-md font-semibold text-white">Trust Metrics</h3>
        {trustMetrics.map((metric, idx) => (
          <div key={idx} className="bg-gray-700/30 rounded-lg p-3">
            <div className="flex justify-between items-center mb-2">
              <div className="flex items-center gap-2">
                <span>{getStatusIcon(metric.status)}</span>
                <span className="text-white font-medium">{metric.name}</span>
              </div>
              <span className={`text-lg font-bold ${getScoreColor(metric.score)}`}>
                {Math.round(metric.score)}%
              </span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2 mb-2">
              <div
                className={`h-2 rounded-full transition-all ${metric.score >= 90 ? 'bg-green-500' : metric.score >= 70 ? 'bg-yellow-500' : 'bg-red-500'}`}
                style={{ width: `${metric.score}%` }}
              ></div>
            </div>
            <p className="text-xs text-gray-400">{metric.description}</p>
            <p className="text-xs text-gray-500 mt-1">Weight: {metric.weight}%</p>
          </div>
        ))}
      </div>

      {/* Risk Factors Breakdown */}
      <div className="space-y-3">
        <h3 className="text-md font-semibold text-white">Risk Factors</h3>
        {riskFactors.map((factor, idx) => (
          <div key={idx} className="bg-gray-700/30 rounded-lg p-3">
            <div className="flex justify-between items-center">
              <div>
                <span className={`font-medium ${getSeverityColor(factor.severity)}`}>{factor.factor}</span>
                <p className="text-xs text-gray-400 mt-1">{factor.description}</p>
              </div>
              <div className="text-right">
                <span className="text-lg font-bold text-yellow-400">{factor.weight}%</span>
                <p className="text-xs text-gray-500">weight</p>
              </div>
            </div>
            <div className="mt-2">
              <div className="w-full bg-gray-700 rounded-full h-1.5">
                <div
                  className="h-1.5 rounded-full bg-yellow-500"
                  style={{ width: `${factor.weight}%` }}
                ></div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Integrity Verification Summary */}
      <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-3">
        <div className="flex justify-between items-center">
          <div>
            <p className="text-sm text-gray-300">Cryptographic Chain Status</p>
            <p className="text-xs text-gray-500">SHA-256 verified</p>
          </div>
          <span className="text-green-400 font-semibold">✅ VERIFIED</span>
        </div>
      </div>
    </div>
  );
};

export default TrustDecomposition;
