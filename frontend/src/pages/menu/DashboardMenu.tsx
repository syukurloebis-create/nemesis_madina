import React from 'react';
import { useDashboardData } from '../../hooks/useDashboardData';

export default function DashboardMenu() {
  const { data, loading, error } = useDashboardData();

  if (loading) return <div className="p-4 text-white">Loading...</div>;
  if (error) return <div className="p-4 text-red-500">Error: {error}</div>;

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-white">Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mt-6">
        <MetricCard title="Total Cases" value={data?.cases?.total || 0} />
        <MetricCard title="Open Cases" value={data?.cases?.open || 0} />
        <MetricCard title="Fraud Alerts" value={data?.fraud?.active_alerts || 0} />
        <MetricCard title="Risk Score" value={data?.risk?.total_risk || 0} />
      </div>
    </div>
  );
}

function MetricCard({ title, value }: { title: string; value: number }) {
  return (
    <div className="bg-gray-800 rounded-xl p-4 border border-gray-700">
      <p className="text-gray-400 text-sm">{title}</p>
      <p className="text-white text-2xl font-bold mt-1">{value}</p>
    </div>
  );
}
