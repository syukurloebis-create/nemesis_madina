// src/pages/ExecutiveDashboard.tsx
import { useEffect, useState } from 'react';
import { useAuthStore } from '../stores/authStore';

const API_URL = 'http://localhost';

interface DashboardStats {
  total_cases: number;
  cases_by_status: Record<string, number>;
  cases_by_priority: Record<string, number>;
  api_instances: number;
  status: string;
}

export default function ExecutiveDashboard() {
  const { token } = useAuthStore();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch(`${API_URL}/api/dashboard/summary`, {
          headers: { 'Authorization': `Bearer ${token}` },
        });
        if (response.ok) {
          const data = await response.json();
          setStats(data);
        }
      } catch (err) {
        console.error('Failed to fetch stats:', err);
      } finally {
        setLoading(false);
      }
    };

    if (token) {
      fetchStats();
    }
  }, [token]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-500 mx-auto"></div>
          <p className="mt-4 text-gray-400">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Executive Dashboard</h1>
        <p className="text-gray-400 mt-1">Real-time forensic intelligence overview</p>
      </div>

      {stats && (
        <>
          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="bg-gray-800/50 rounded-lg p-6 border border-gray-700">
              <div className="text-3xl font-bold text-cyan-400">{stats.total_cases}</div>
              <div className="text-gray-400 mt-1">Total Cases</div>
            </div>
            <div className="bg-gray-800/50 rounded-lg p-6 border border-gray-700">
              <div className="text-3xl font-bold text-green-400">
                {stats.cases_by_status?.open || 0}
              </div>
              <div className="text-gray-400 mt-1">Open Cases</div>
            </div>
            <div className="bg-gray-800/50 rounded-lg p-6 border border-gray-700">
              <div className="text-3xl font-bold text-red-400">
                {stats.cases_by_priority?.critical || 0}
              </div>
              <div className="text-gray-400 mt-1">Critical Priority</div>
            </div>
            <div className="bg-gray-800/50 rounded-lg p-6 border border-gray-700">
              <div className="text-3xl font-bold text-purple-400">
                {stats.api_instances || 1}
              </div>
              <div className="text-gray-400 mt-1">API Instances</div>
            </div>
          </div>

          {/* Cases by Status */}
          <div className="bg-gray-800/50 rounded-lg p-6 border border-gray-700">
            <h2 className="text-lg font-semibold text-white mb-4">Cases by Status</h2>
            <div className="flex flex-wrap gap-3">
              {Object.entries(stats.cases_by_status || {}).map(([status, count]) => (
                <div key={status} className="px-3 py-1 bg-gray-700 rounded-full text-sm">
                  <span className="text-gray-300">{status}:</span>{' '}
                  <span className="text-cyan-400 font-semibold">{count as number}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Cases by Priority */}
          <div className="bg-gray-800/50 rounded-lg p-6 border border-gray-700">
            <h2 className="text-lg font-semibold text-white mb-4">Cases by Priority</h2>
            <div className="flex flex-wrap gap-3">
              {Object.entries(stats.cases_by_priority || {}).map(([priority, count]) => (
                <div key={priority} className="px-3 py-1 bg-gray-700 rounded-full text-sm">
                  <span className="text-gray-300">{priority}:</span>{' '}
                  <span className="text-cyan-400 font-semibold">{count as number}</span>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}