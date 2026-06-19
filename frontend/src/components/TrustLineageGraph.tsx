// src/components/TrustLineageGraph.tsx
import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { api } from '@/services/api';

export const TrustLineageGraph: React.FC<{ aggregateId: string }> = ({ aggregateId }) => {
  const { data, isLoading } = useQuery({
    queryKey: ['trustLineage', aggregateId],
    queryFn: () => api.getTrustLineage(aggregateId),
    enabled: !!aggregateId,
  });

  if (isLoading) return <div>Loading trust lineage...</div>;
  if (!data) return null;

  const { trust_status, trust_icon, risk_score, risk_level, risk_drivers, event_count, chain_integrity } = data;

  return (
    <div className="bg-gray-900 rounded-xl p-6 border border-cyan-500/30">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-bold text-white">Trust Lineage Analysis</h3>
        <div className="flex items-center gap-2">
          <span className="text-2xl">{trust_icon}</span>
          <span className={`text-sm font-medium ${trust_status === 'VERIFIED' ? 'text-green-400' : 'text-red-400'}`}>
            {trust_status}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Risk Score Card */}
        <div className="bg-gray-800/50 rounded-lg p-4">
          <div className="text-sm text-gray-400 mb-1">Risk Score</div>
          <div className="text-3xl font-bold text-orange-400">{(risk_score * 100).toFixed(0)}%</div>
          <div className={`text-xs mt-1 ${risk_level === 'HIGH' ? 'text-red-400' : risk_level === 'MEDIUM' ? 'text-yellow-400' : 'text-green-400'}`}>
            {risk_level} RISK
          </div>
        </div>

        {/* Chain Integrity */}
        <div className="bg-gray-800/50 rounded-lg p-4">
          <div className="text-sm text-gray-400 mb-1">Chain Integrity</div>
          <div className="text-2xl font-bold text-cyan-400">{chain_integrity ? '100%' : '0%'}</div>
          <div className="text-xs text-gray-500 mt-1">{event_count} events in chain</div>
        </div>
      </div>

      {/* Risk Drivers */}
      <div className="mt-6">
        <h4 className="text-sm font-semibold text-gray-400 mb-3">Risk Drivers</h4>
        <div className="space-y-2">
          {risk_drivers.map((driver, idx) => (
            <div key={idx} className="flex items-center justify-between p-2 bg-gray-800/30 rounded">
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-500">Event #{driver.sequence}</span>
                <span className="text-sm text-white">{driver.factor}</span>
              </div>
              <span className="text-sm text-orange-400">{driver.contribution}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Evidence Chain */}
      <div className="mt-6 pt-4 border-t border-gray-800">
        <div className="text-sm text-gray-400 mb-3">Evidence Chain</div>
        <div className="flex items-center gap-2 flex-wrap">
          {[...Array(event_count)].map((_, i) => (
            <React.Fragment key={i}>
              <div className="w-8 h-8 rounded-full bg-cyan-500/20 flex items-center justify-center text-cyan-400 text-sm">
                {i + 1}
              </div>
              {i < event_count - 1 && <span className="text-gray-600">→</span>}
            </React.Fragment>
          ))}
        </div>
      </div>
    </div>
  );
};