import React from 'react';
import RiskMetrics from '../components/analytics/RiskMetrics';
import TrendChart from '../components/analytics/TrendChart';

const Analytics: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="bg-gray-800/50 rounded-xl p-4 border border-gray-700">
        <h1 className="text-2xl font-bold text-white">Analytics & Intelligence</h1>
        <p className="text-gray-400 text-sm mt-1">Risk analysis, trend monitoring, and predictive insights</p>
      </div>

      {/* Risk Metrics Section */}
      <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-700">
          <h2 className="text-lg font-semibold text-white">Risk Intelligence</h2>
          <p className="text-xs text-gray-500 mt-1">Entity risk scoring and distribution analysis</p>
        </div>
        <div className="p-4">
          <RiskMetrics />
        </div>
      </div>

      {/* Trend Analysis Section */}
      <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-700">
          <h2 className="text-lg font-semibold text-white">Trend Analysis</h2>
          <p className="text-xs text-gray-500 mt-1">Case creation, resolution, and risk score trends</p>
        </div>
        <div className="p-4">
          <TrendChart />
        </div>
      </div>

      {/* Key Insights */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-gray-800 rounded-xl p-4 border border-gray-700">
          <h3 className="font-semibold text-white mb-2">Key Insights</h3>
          <ul className="space-y-2 text-sm text-gray-400">
            <li>• Average case resolution time: 5.2 days</li>
            <li>• High risk entities increased by 15%</li>
            <li>• Integrity score maintained at 100%</li>
            <li>• 98% of evidence cryptographically verified</li>
          </ul>
        </div>
        <div className="bg-gray-800 rounded-xl p-4 border border-gray-700">
          <h3 className="font-semibold text-white mb-2">Recommendations</h3>
          <ul className="space-y-2 text-sm text-gray-400">
            <li>• Priority investigation on critical risk entities</li>
            <li>• Enhanced monitoring for high-risk patterns</li>
            <li>• Regular hash chain verification audit</li>
            <li>• Continuous integrity monitoring</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default Analytics;
