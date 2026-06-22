// src/components/dashboard/layers/EvidenceCenter.tsx
import React from 'react';

interface EvidenceCenterProps {
  stats: any;
}

export const EvidenceCenter: React.FC<EvidenceCenterProps> = ({ stats }) => {
  const total = stats?.total || 0;
  const pending = stats?.pending || 0;
  const verified = stats?.verified || 0;
  const rejected = stats?.rejected || 0;
  const trustScore = stats?.trust_score || 0;

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800 dark:text-white">Evidence Center</h2>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <p className="text-sm text-gray-500 dark:text-gray-400">Total</p>
          <p className="text-2xl font-bold text-gray-800 dark:text-white">{total}</p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <p className="text-sm text-gray-500 dark:text-gray-400">Pending</p>
          <p className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">{pending}</p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <p className="text-sm text-gray-500 dark:text-gray-400">Verified</p>
          <p className="text-2xl font-bold text-green-600 dark:text-green-400">{verified}</p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <p className="text-sm text-gray-500 dark:text-gray-400">Rejected</p>
          <p className="text-2xl font-bold text-red-600 dark:text-red-400">{rejected}</p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <p className="text-sm text-gray-500 dark:text-gray-400">Trust Score</p>
          <p className="text-2xl font-bold text-blue-600 dark:text-blue-400">{trustScore}%</p>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 text-center">
        <p className="text-gray-500 dark:text-gray-400">
          {total === 0 ? 'No evidence uploaded yet.' : `${total} evidence items uploaded.`}
        </p>
        <p className="text-sm text-gray-400 dark:text-gray-500 mt-2">
          {total === 0 ? 'Upload evidence to start building your case.' : `${verified} verified, ${pending} pending review.`}
        </p>
      </div>
    </div>
  );
};

export default EvidenceCenter;