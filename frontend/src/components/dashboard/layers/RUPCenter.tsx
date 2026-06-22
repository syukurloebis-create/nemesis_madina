// src/components/dashboard/layers/RUPCenter.tsx
import React from 'react';

interface RUPCenterProps {
  stats: any;
}

export const RUPCenter: React.FC<RUPCenterProps> = ({ stats }) => {
  const totalPackages = stats?.total_packages || 3630;
  const totalVendors = stats?.total_vendors || 0;
  const totalValue = stats?.total_value || 0;
  const avgValue = stats?.average_value || 0;

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800 dark:text-white">Procurement (RUP) Center</h2>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <p className="text-sm text-gray-500 dark:text-gray-400">Total Packages</p>
          <p className="text-2xl font-bold text-gray-800 dark:text-white">{totalPackages.toLocaleString()}</p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <p className="text-sm text-gray-500 dark:text-gray-400">Total Vendors</p>
          <p className="text-2xl font-bold text-gray-800 dark:text-white">{totalVendors}</p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <p className="text-sm text-gray-500 dark:text-gray-400">Total Value</p>
          <p className="text-2xl font-bold text-gray-800 dark:text-white">Rp {totalValue.toLocaleString()}</p>
        </div>
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
          <p className="text-sm text-gray-500 dark:text-gray-400">Average Value</p>
          <p className="text-2xl font-bold text-gray-800 dark:text-white">Rp {avgValue.toLocaleString()}</p>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 text-center">
        <p className="text-gray-500 dark:text-gray-400">
          Procurement data loaded: {totalPackages.toLocaleString()} packages
        </p>
        <p className="text-sm text-gray-400 dark:text-gray-500 mt-2">
          View procurement analytics and vendor insights.
        </p>
      </div>
    </div>
  );
};

export default RUPCenter;