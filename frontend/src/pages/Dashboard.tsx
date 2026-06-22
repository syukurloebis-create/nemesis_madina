import React from 'react';
import { useDashboardData } from '../hooks/useDashboardData';

const Dashboard: React.FC = () => {
  const caseId = '446e216d-eb0e-487e-8e6b-ec943468ea20';
  const { data, loading, error, refresh } = useDashboardData(caseId);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50 dark:bg-gray-900">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
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

  return (
    <div className="min-h-screen bg-dark-bg text-white">
      <div className="container mx-auto p-6">
        <h1 className="text-3xl font-bold gradient-text">NEMESIS V8+</h1>
        <p className="text-gray-400">Intelligence Dashboard</p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mt-6">
          <div className="bg-dark-card p-4 rounded-lg">
            <h3 className="text-sm text-gray-400">Total Cases</h3>
            <p className="text-2xl font-bold">{data?.cases?.length || 0}</p>
          </div>
          <div className="bg-dark-card p-4 rounded-lg">
            <h3 className="text-sm text-gray-400">Risk Score</h3>
            <p className="text-2xl font-bold">{data?.risk?.score || 0}%</p>
          </div>
          <div className="bg-dark-card p-4 rounded-lg">
            <h3 className="text-sm text-gray-400">Key Actors</h3>
            <p className="text-2xl font-bold">{data?.actors?.length || 0}</p>
          </div>
          <div className="bg-dark-card p-4 rounded-lg">
            <h3 className="text-sm text-gray-400">Recommendations</h3>
            <p className="text-2xl font-bold">{data?.recommendations?.length || 0}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
