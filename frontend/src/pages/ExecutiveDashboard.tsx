import React, { useState } from 'react';
import { useDashboardData } from '../hooks/useDashboardData';
import { RefreshCw, Activity } from 'lucide-react';
import ExecutiveKPICards from '../components/dashboard/ExecutiveKPICards';

export default function ExecutiveDashboard() {
  const { data, loading, error, refetch, isRefreshing } = useDashboardData();
  const [activeTab, setActiveTab] = useState('overview');

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto" />
          <p className="mt-4 text-gray-400">Loading Executive Dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-900">
        <div className="text-center">
          <p className="text-red-400">⚠️ Failed to load dashboard</p>
          <button
            onClick={() => refetch()}
            className="mt-4 px-4 py-2 bg-blue-600 rounded-lg hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const isHealthy = data?.health?.status === 'healthy';

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Header */}
      <header className="bg-gray-800/80 backdrop-blur-sm border-b border-gray-700 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">N</span>
            </div>
            <div>
              <h1 className="text-lg font-bold text-white">Executive Dashboard</h1>
              <p className="text-xs text-gray-400">NEMESIS Intelligence Center</p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-sm">
              <span className={`w-2 h-2 rounded-full ${isHealthy ? 'bg-green-500' : 'bg-red-500'}`} />
              <span className="text-gray-400">{isHealthy ? 'Operational' : 'Degraded'}</span>
            </div>
            <button
              onClick={() => refetch()}
              disabled={isRefreshing}
              className="flex items-center gap-1.5 px-3 py-1.5 text-sm text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
              Refresh
            </button>
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-6 py-6 space-y-6">
        {/* KPI Cards */}
        <ExecutiveKPICards
          cases={data?.cases}
          fraud={data?.fraud}
          graph={data?.graph}
          risk={data?.risk}
        />

        {/* Tabs */}
        <div className="flex gap-1 border-b border-gray-800 pb-2">
          {['Overview', 'Risk', 'Fraud', 'Graph', 'Intelligence'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab.toLowerCase())}
              className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                activeTab === tab.toLowerCase()
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-400 hover:text-white hover:bg-gray-800'
              }`}
            >
              {tab}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Risk Panel */}
          <div className="bg-gray-800/50 rounded-xl border border-gray-700 p-6">
            <h3 className="text-lg font-semibold text-white mb-4">📊 Risk Overview</h3>
            <div className="space-y-3">
              <RiskBar label="Total Risk" value={data?.risk?.total_risk ?? 0} max={100} />
              <RiskBar label="High Risk" value={data?.risk?.high_risk ?? 0} max={data?.risk?.total_risk || 100} />
              <RiskBar label="Medium Risk" value={data?.risk?.medium_risk ?? 0} max={data?.risk?.total_risk || 100} />
            </div>
          </div>

          {/* Fraud Panel */}
          <div className="bg-gray-800/50 rounded-xl border border-gray-700 p-6">
            <h3 className="text-lg font-semibold text-white mb-4">🚨 Fraud Intelligence</h3>
            <div className="grid grid-cols-2 gap-4">
              <MetricBox label="Total" value={data?.fraud?.total ?? 0} />
              <MetricBox label="High Confidence" value={data?.fraud?.high_confidence ?? 0} color="red" />
              <MetricBox label="Active Alerts" value={data?.fraud?.active_alerts ?? 0} color="orange" />
              <MetricBox label="Collusion" value={data?.fraud?.collusion ?? 0} color="purple" />
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex justify-between items-center text-xs text-gray-500 pt-4 border-t border-gray-800">
          <span>NEMESIS V8.1 — Strategic Intelligence Center</span>
          <span>{data?.health?.version ?? '8.1.0'}</span>
        </div>
      </main>
    </div>
  );
}

// ============================================================
// COMPONENTS
// ============================================================

function RiskBar({ label, value, max }: { label: string; value: number; max: number }) {
  const percentage = max > 0 ? (value / max) * 100 : 0;
  const color = percentage > 70 ? 'bg-red-500' : percentage > 40 ? 'bg-yellow-500' : 'bg-green-500';

  return (
    <div>
      <div className="flex justify-between text-sm">
        <span className="text-gray-400">{label}</span>
        <span className="text-white">{value}</span>
      </div>
      <div className="w-full h-1.5 bg-gray-700 rounded-full mt-1 overflow-hidden">
        <div className={`h-full rounded-full ${color}`} style={{ width: `${Math.min(percentage, 100)}%` }} />
      </div>
    </div>
  );
}

function MetricBox({ label, value, color = 'blue' }: { label: string; value: number; color?: string }) {
  const colors = {
    blue: 'text-blue-400',
    red: 'text-red-400',
    orange: 'text-orange-400',
    purple: 'text-purple-400',
    green: 'text-green-400',
  };

  return (
    <div className="bg-gray-900/50 rounded-lg p-3 text-center">
      <p className={`text-2xl font-bold ${colors[color as keyof typeof colors]}`}>{value}</p>
      <p className="text-xs text-gray-400">{label}</p>
    </div>
  );
}
