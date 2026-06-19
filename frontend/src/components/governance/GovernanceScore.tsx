// src/components/governance/GovernanceScore.tsx
import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';
import { Shield, CheckCircle, AlertTriangle } from 'lucide-react';

interface GovernanceScoreProps {
  caseId?: string;
}

const GovernanceScore: React.FC<GovernanceScoreProps> = ({ caseId }) => {
  const [score, setScore] = useState(0);
  const [metrics, setMetrics] = useState({
    chainIntegrity: 0,
    evidenceVerification: 0,
    custodyCompliance: 0,
    auditTrail: 0,
    timestampValidity: 0
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadGovernanceData();
  }, [caseId]);

  const loadGovernanceData = async () => {
    setLoading(true);
    try {
      let chainScore = 100;
      if (caseId) {
        const integrity = await api.verifyCaseIntegrity(caseId);
        chainScore = integrity.status === 'PASS' ? 100 : 0;
      } else {
        const allIntegrity = await api.verifyAllIntegrity();
        const totalCases = allIntegrity.total_cases || 1;
        const passedCases = allIntegrity.passed_cases || 0;
        chainScore = (passedCases / totalCases) * 100;
      }

      let evidenceScore = 100;
      if (caseId) {
        const evidenceList = await api.listEvidence(caseId);
        const evidence = evidenceList.evidence || [];
        if (evidence.length > 0) {
          let verifiedCount = 0;
          for (const ev of evidence) {
            try {
              const verifyResult = await api.verifyEvidence(ev.id);
              if (verifyResult.status === 'VERIFIED') verifiedCount++;
            } catch (e) { }
          }
          evidenceScore = (verifiedCount / evidence.length) * 100;
        }
      }

      let custodyScore = 100;
      if (caseId) {
        const evidenceList = await api.listEvidence(caseId);
        const evidence = evidenceList.evidence || [];
        if (evidence.length > 0) {
          let hasCustodyCount = 0;
          for (const ev of evidence) {
            try {
              const history = await api.getCustodyHistory(ev.id);
              if (history.history && history.history.length > 0) hasCustodyCount++;
            } catch (e) { }
          }
          custodyScore = (hasCustodyCount / evidence.length) * 100;
        }
      }

      const auditScore = 95;
      const timestampScore = 100;

      const totalScore = Math.round(
        (chainScore * 0.35) +
        (evidenceScore * 0.25) +
        (custodyScore * 0.2) +
        (auditScore * 0.1) +
        (timestampScore * 0.1)
      );

      setMetrics({
        chainIntegrity: chainScore,
        evidenceVerification: evidenceScore,
        custodyCompliance: custodyScore,
        auditTrail: auditScore,
        timestampValidity: timestampScore
      });
      setScore(totalScore);
    } catch (error) {
      console.error('Error loading governance data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = () => {
    if (score >= 90) return 'text-green-600';
    if (score >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBgColor = () => {
    if (score >= 90) return 'bg-green-100';
    if (score >= 70) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  const getMetricIcon = (value: number) => {
    if (value >= 90) return <CheckCircle className="w-4 h-4 text-green-500" />;
    return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6 animate-pulse">
        <div className="h-32 bg-gray-200 rounded"></div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center gap-2 mb-4">
        <Shield className="w-5 h-5 text-blue-600" />
        <h3 className="text-lg font-semibold text-gray-900">Governance Score</h3>
      </div>

      <div className="flex items-center justify-center mb-6">
        <div className={`w-32 h-32 rounded-full ${getScoreBgColor()} flex items-center justify-center`}>
          <div className="text-center">
            <div className={`text-3xl font-bold ${getScoreColor()}`}>{score}</div>
            <div className="text-xs text-gray-500">out of 100</div>
          </div>
        </div>
      </div>

      <div className="space-y-3">
        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-600">Chain Integrity</span>
            <span className="flex items-center gap-1">{getMetricIcon(metrics.chainIntegrity)} {Math.round(metrics.chainIntegrity)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div className="bg-blue-600 h-2 rounded-full" style={{ width: `${metrics.chainIntegrity}%` }}></div>
          </div>
        </div>
        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-600">Evidence Verification</span>
            <span className="flex items-center gap-1">{getMetricIcon(metrics.evidenceVerification)} {Math.round(metrics.evidenceVerification)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div className="bg-green-600 h-2 rounded-full" style={{ width: `${metrics.evidenceVerification}%` }}></div>
          </div>
        </div>
        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-600">Custody Compliance</span>
            <span className="flex items-center gap-1">{getMetricIcon(metrics.custodyCompliance)} {Math.round(metrics.custodyCompliance)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div className="bg-purple-600 h-2 rounded-full" style={{ width: `${metrics.custodyCompliance}%` }}></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GovernanceScore;