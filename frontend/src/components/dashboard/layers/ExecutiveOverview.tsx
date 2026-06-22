// src/components/dashboard/layers/ExecutiveOverview.tsx
import React from 'react';

interface ExecutiveOverviewProps {
  cases: any[];
  stats: any;
  graphData: any;
}

export const ExecutiveOverview: React.FC<ExecutiveOverviewProps> = ({ cases, stats, graphData }) => {
  const totalCases = stats?.total || cases?.length || 0;
  const openCases = stats?.open || 0;
  const criticalCases = cases?.filter((c: any) => c.priority === 'CRITICAL').length || 0;
  const avgRiskScore = cases?.length > 0
    ? (cases.reduce((acc: number, c: any) => acc + (c.risk_score || 0), 0) / cases.length).toFixed(1)
    : '0.0';

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800 dark:text-white">Executive Overview</h2>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <p className="text-sm text-gray-500 dark:text-gray-400">Total Cases</p>
          <p className="text-2xl font-bold text-gray-800 dark:text-white">{totalCases}</p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <p className="text-sm text-gray-500 dark:text-gray-400">Open Cases</p>
          <p className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">{openCases}</p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <p className="text-sm text-gray-500 dark:text-gray-400">Critical</p>
          <p className="text-2xl font-bold text-red-600 dark:text-red-400">{criticalCases}</p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <p className="text-sm text-gray-500 dark:text-gray-400">Avg Risk Score</p>
          <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">{avgRiskScore}</p>
        </div>
      </div>

      {/* Recent Cases */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <h3 className="text-lg font-semibold text-gray-800 dark:text-white">Recent Cases</h3>
        </div>
        <div className="divide-y divide-gray-200 dark:divide-gray-700">
          {cases?.slice(0, 5).map((caseItem: any) => (
            <div key={caseItem.id} className="p-4 flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-800 dark:text-white">{caseItem.title}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {caseItem.status} • {caseItem.workflow_stage}
                </p>
              </div>
              <div className="flex items-center gap-3">
                <span className={`px-2 py-1 text-xs rounded-full ${
                  caseItem.risk_level === 'HIGH'
                    ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                    : caseItem.risk_level === 'MEDIUM'
                    ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                    : 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                }`}>
                  {caseItem.risk_level || 'LOW'}
                </span>
                <span className="text-sm font-bold text-gray-700 dark:text-gray-300">
                  {caseItem.risk_score || 0}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ExecutiveOverview;