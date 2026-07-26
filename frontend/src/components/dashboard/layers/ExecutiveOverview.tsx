import React from 'react';
import { ExecutiveData, StatsData } from '@/types/dashboard';

interface ExecutiveOverviewProps {
  data: ExecutiveData;
  stats: StatsData;
  loading: boolean;
}

const ExecutiveOverview: React.FC<ExecutiveOverviewProps> = ({ data, stats, loading }) => {
  if (loading) {
    return <div className="p-4 bg-gray-100 dark:bg-gray-800 rounded-lg animate-pulse">Loading...</div>;
  }

  return (
    <div className="bg-white dark:bg-dark-card rounded-lg shadow p-4">
      <h2 className="text-xl font-bold mb-4">Executive Overview</h2>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard label="Total Cases" value={data.totalCases} />
        <MetricCard label="Active Cases" value={data.activeCases} />
        <MetricCard label="High Risk" value={data.highRiskCases} />
        <MetricCard label="Critical Alerts" value={data.criticalAlerts} />
      </div>
    </div>
  );
};

const MetricCard: React.FC<{ label: string; value: number }> = ({ label, value }) => (
  <div className="bg-gray-50 dark:bg-gray-800 p-3 rounded">
    <p className="text-sm text-gray-500">{label}</p>
    <p className="text-2xl font-bold">{value}</p>
  </div>
);

export default ExecutiveOverview;
