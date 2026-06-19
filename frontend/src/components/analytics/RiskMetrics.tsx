import React, { useEffect, useState } from 'react';
import { useAuthStore } from '../../stores/authStore';

interface RiskData {
  total_entities: number;
  avg_risk_score: number;
  distribution: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
  top_risk_entities: Array<{
    entity_id: string;
    entity_name: string;
    risk_score: number;
    risk_level: string;
  }>;
}

const RiskMetrics: React.FC = () => {
  const [riskData, setRiskData] = useState<RiskData | null>(null);
  const [loading, setLoading] = useState(true);
  const { token } = useAuthStore();

  useEffect(() => {
    fetchRiskData();
  }, []);

  const fetchRiskData = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost/risk-metrics/summary', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setRiskData(data);
      } else {
        // Mock data
        setRiskData({
          total_entities: 25,
          avg_risk_score: 68,
          distribution: { critical: 4, high: 7, medium: 10, low: 4 },
          top_risk_entities: [
            { entity_id: '1', entity_name: 'PT. Maju Jaya', risk_score: 92, risk_level: 'critical' },
            { entity_id: '2', entity_name: 'CV. Karya Mandiri', risk_score: 88, risk_level: 'high' },
            { entity_id: '3', entity_name: 'PT. Bangun Nusantara', risk_score: 78, risk_level: 'high' },
            { entity_id: '4', entity_name: 'Kementerian PUPR', risk_score: 65, risk_level: 'medium' },
            { entity_id: '5', entity_name: 'Dr. Ahmad Fauzi', risk_score: 58, risk_level: 'medium' },
          ]
        });
      }
    } catch (error) {
      console.error('Failed to fetch risk data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (score: number) => {
    if (score >= 85) return 'text-red-500';
    if (score >= 70) return 'text-orange-500';
    if (score >= 40) return 'text-yellow-500';
    return 'text-green-500';
  };

  const getRiskBgColor = (score: number) => {
    if (score >= 85) return 'bg-red-500/20';
    if (score >= 70) return 'bg-orange-500/20';
    if (score >= 40) return 'bg-yellow-500/20';
    return 'bg-green-500/20';
  };

  if (loading) {
    return <div className="text-center py-8 text-gray-400">Loading risk metrics...</div>;
  }

  if (!riskData) {
    return <div className="text-center py-8 text-gray-500">No risk data available</div>;
  }

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gray-800 rounded-xl p-4 border border-gray-700">
          <p className="text-gray-400 text-sm">Total Entities</p>
          <p className="text-2xl font-bold text-white">{riskData.total_entities}</p>
        </div>
        <div className="bg-gray-800 rounded-xl p-4 border border-gray-700">
          <p className="text-gray-400 text-sm">Average Risk Score</p>
          <p className={`text-2xl font-bold ${getRiskColor(riskData.avg_risk_score)}`}>
            {riskData.avg_risk_score}%
          </p>
        </div>
        <div className="bg-gray-800 rounded-xl p-4 border border-gray-700">
          <p className="text-gray-400 text-sm">Risk Distribution</p>
          <div className="flex gap-2 mt-1">
            <span className="text-xs text-red-400">C:{riskData.distribution.critical}</span>
            <span className="text-xs text-orange-400">H:{riskData.distribution.high}</span>
            <span className="text-xs text-yellow-400">M:{riskData.distribution.medium}</span>
            <span className="text-xs text-green-400">L:{riskData.distribution.low}</span>
          </div>
        </div>
      </div>

      {/* Risk Distribution Bar */}
      <div className="bg-gray-800 rounded-xl p-4 border border-gray-700">
        <h4 className="font-semibold text-white mb-3">Risk Distribution</h4>
        <div className="space-y-2">
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-red-400">Critical</span>
              <span>{riskData.distribution.critical}</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div className="bg-red-500 h-2 rounded-full" style={{ width: `${(riskData.distribution.critical / riskData.total_entities) * 100}%` }}></div>
            </div>
          </div>
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-orange-400">High</span>
              <span>{riskData.distribution.high}</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div className="bg-orange-500 h-2 rounded-full" style={{ width: `${(riskData.distribution.high / riskData.total_entities) * 100}%` }}></div>
            </div>
          </div>
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-yellow-400">Medium</span>
              <span>{riskData.distribution.medium}</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div className="bg-yellow-500 h-2 rounded-full" style={{ width: `${(riskData.distribution.medium / riskData.total_entities) * 100}%` }}></div>
            </div>
          </div>
          <div>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-green-400">Low</span>
              <span>{riskData.distribution.low}</span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div className="bg-green-500 h-2 rounded-full" style={{ width: `${(riskData.distribution.low / riskData.total_entities) * 100}%` }}></div>
            </div>
          </div>
        </div>
      </div>

      {/* Top Risk Entities */}
      <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
        <div className="px-4 py-3 border-b border-gray-700">
          <h4 className="font-semibold text-white">Top Risk Entities</h4>
        </div>
        <div className="divide-y divide-gray-700">
          {riskData.top_risk_entities.map((entity) => (
            <div key={entity.entity_id} className="p-3 flex justify-between items-center">
              <div>
                <p className="font-medium text-white">{entity.entity_name}</p>
                <p className="text-xs text-gray-500">ID: {entity.entity_id.slice(0, 8)}...</p>
              </div>
              <div className={`px-3 py-1 rounded-full text-sm font-semibold ${getRiskBgColor(entity.risk_score)} ${getRiskColor(entity.risk_score)}`}>
                {entity.risk_score}%
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default RiskMetrics;
