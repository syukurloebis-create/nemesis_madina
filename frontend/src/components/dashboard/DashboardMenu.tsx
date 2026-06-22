// src/components/dashboard/DashboardMenu.tsx
import React, { useState } from 'react';
import { useDashboardData } from '../../hooks/useDashboardData';
import { ExecutiveOverview } from './layers/ExecutiveOverview';
import { CasesCenter } from './layers/CasesCenter';
import { EvidenceCenter } from './layers/EvidenceCenter';
import { GraphCenter } from './layers/GraphCenter';
import { FraudCenter } from './layers/FraudCenter';
import { RUPCenter } from './layers/RUPCenter';
import { AIStatusBar } from '../intelligence/AIStatusBar';

interface MenuItem {
  id: string;
  label: string;
  icon: string;
}

const menuItems: MenuItem[] = [
  { id: 'executive', label: 'Executive Overview', icon: '📊' },
  { id: 'cases', label: 'Cases Center', icon: '📋' },
  { id: 'evidence', label: 'Evidence Center', icon: '📎' },
  { id: 'graph', label: 'Network Intelligence', icon: '🕸️' },
  { id: 'fraud', label: 'Fraud Center', icon: '🚨' },
  { id: 'rup', label: 'Procurement (RUP)', icon: '📦' },
];

export const DashboardMenu: React.FC = () => {
  const [activeLayer, setActiveLayer] = useState('executive');
  const { cases, stats, graphData, evidenceStats, procurementStats, loading, error, refresh } = useDashboardData();

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-500 dark:text-gray-400">Loading NEMESIS Dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50 dark:bg-gray-900">
        <div className="text-center p-6 bg-red-50 dark:bg-red-900/20 rounded-lg">
          <p className="text-red-600 dark:text-red-400">❌ Error: {error}</p>
          <button
            onClick={refresh}
            className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const renderLayer = () => {
    switch (activeLayer) {
      case 'executive':
        return <ExecutiveOverview cases={cases} stats={stats} graphData={graphData} />;
      case 'cases':
        return <CasesCenter cases={cases} stats={stats} />;
      case 'evidence':
        return <EvidenceCenter stats={evidenceStats} />;
      case 'graph':
        return <GraphCenter graphData={graphData} />;
      case 'fraud':
        return <FraudCenter graphData={graphData} />;
      case 'rup':
        return <RUPCenter stats={procurementStats} />;
      default:
        return <ExecutiveOverview cases={cases} stats={stats} graphData={graphData} />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <AIStatusBar isActive={true} lastUpdate={new Date().toISOString()} />

      {/* Navigation */}
      <div className="border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 px-4">
        <div className="flex space-x-1 overflow-x-auto py-2">
          {menuItems.map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveLayer(item.id)}
              className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors whitespace-nowrap ${
                activeLayer === item.id
                  ? 'bg-blue-500/10 text-blue-600 dark:text-blue-400 border-b-2 border-blue-500'
                  : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'
              }`}
            >
              <span className="mr-2">{item.icon}</span>
              {item.label}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        <div className="max-w-7xl mx-auto">
          {renderLayer()}
        </div>
      </div>
    </div>
  );
};