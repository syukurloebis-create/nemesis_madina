import React from 'react';
import { useDashboard } from '@/context/DashboardContext';
import ExecutiveOverview from './layers/ExecutiveOverview';
import CasesCenter from './layers/CasesCenter';
import EvidenceCenter from './layers/EvidenceCenter';
import GraphCenter from './layers/GraphCenter';
import FraudCenter from './layers/FraudCenter';
import RUPCenter from './layers/RUPCenter';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { ErrorBoundary } from '@/components/ui/ErrorBoundary';

export const DashboardMenu: React.FC = () => {
  const { data, loading, error, refresh, isStale } = useDashboard();

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <LoadingSpinner text="Loading dashboard data..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-screen">
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

  if (!data) {
    return (
      <div className="flex items-center justify-center h-screen">
        <p className="text-gray-500">No data available</p>
      </div>
    );
  }

  return (
    <ErrorBoundary>
      <div className="space-y-4 p-4">
        {/* Stale indicator */}
        {isStale && (
          <div className="bg-yellow-50 dark:bg-yellow-900/20 p-2 rounded text-center text-sm">
            ⏳ Data is being refreshed...
          </div>
        )}

        {/* Dashboard Layers */}
        <div className="grid grid-cols-1 gap-4">
          <ExecutiveOverview 
            data={data.executive} 
            stats={data.stats}
            loading={loading}
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <CasesCenter 
            data={data.cases}
            stats={data.stats}
            loading={loading}
          />
          <EvidenceCenter 
            data={data.evidence}
            loading={loading}
          />
        </div>

        <div className="grid grid-cols-1 gap-4">
          <GraphCenter 
            data={data.graph}
            loading={loading}
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FraudCenter 
            data={data.fraud}
            loading={loading}
          />
          <RUPCenter 
            data={data.rup}
            loading={loading}
          />
        </div>
      </div>
    </ErrorBoundary>
  );
};

export default DashboardMenu;
