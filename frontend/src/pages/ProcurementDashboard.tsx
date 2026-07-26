import React, { useState, useEffect } from 'react';
import { api } from '../services/api';

interface ProcurementPackage {
  id: string;
  title: string;
  vendor: string;
  amount: number;
  status: string;
}

interface ProcurementStats {
  total: number;
  active: number;
  completed: number;
  total_value: number;
}

export default function ProcurementDashboard() {
  const [packages, setPackages] = useState<ProcurementPackage[]>([]);
  const [stats, setStats] = useState<ProcurementStats>({
    total: 0,
    active: 0,
    completed: 0,
    total_value: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        const [packagesRes, statsRes] = await Promise.all([
          api.get('/api/v1/procurement/packages'),
          api.get('/api/v1/procurement/stats'),
        ]);
        setPackages(packagesRes?.data || []);
        setStats(statsRes?.data || { total: 0, active: 0, completed: 0, total_value: 0 });
      } catch (error) {
        console.error('Failed to load procurement data:', error);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  if (loading) {
    return <div className="p-6 text-white">Loading procurement data...</div>;
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-white">Procurement Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-6">
        <StatCard label="Total" value={stats.total} />
        <StatCard label="Active" value={stats.active} />
        <StatCard label="Completed" value={stats.completed} />
        <StatCard label="Total Value" value={`Rp ${(stats.total_value / 1000000000).toFixed(1)}B`} />
      </div>
      <div className="mt-6 bg-gray-800 rounded-xl border border-gray-700 p-4">
        <h2 className="text-white font-semibold">Recent Packages</h2>
        {packages.length === 0 ? (
          <p className="text-gray-400 mt-2">No packages found</p>
        ) : (
          <ul className="mt-2 space-y-2">
            {packages.slice(0, 5).map((pkg) => (
              <li key={pkg.id} className="text-gray-300 border-b border-gray-700 pb-2">
                {pkg.title} - {pkg.vendor} (Rp {(pkg.amount / 1000000).toFixed(1)}M)
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: number | string }) {
  return (
    <div className="bg-gray-800 rounded-xl p-4 border border-gray-700">
      <p className="text-gray-400 text-sm">{label}</p>
      <p className="text-white text-2xl font-bold mt-1">{value}</p>
    </div>
  );
}
