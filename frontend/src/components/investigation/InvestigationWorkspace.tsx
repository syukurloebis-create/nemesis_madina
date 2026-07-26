import React, { useState, useEffect } from 'react';
import { investigationService } from '../../services/investigations';

interface Investigation {
  id: string;
  case_id: string;
  title: string;
  status: string;
  priority: string;
  assigned_to?: string;
  created_at: string;
  updated_at: string;
}

interface InvestigationStats {
  total: number;
  active: number;
  completed: number;
  pending: number;
}

export function InvestigationWorkspace() {
  const [investigations, setInvestigations] = useState<Investigation[]>([]);
  const [stats, setStats] = useState<InvestigationStats>({
    total: 0,
    active: 0,
    completed: 0,
    pending: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [investigationsRes, statsRes] = await Promise.all([
        investigationService.getByCase('all'),
        investigationService.getStats('all'),
      ]);

      const investigationsData = investigationsRes?.data || investigationsRes || [];
      const statsData = statsRes?.data || statsRes || {};

      setInvestigations(Array.isArray(investigationsData) ? investigationsData : []);
      setStats({
        total: statsData.total || 0,
        active: statsData.active || 0,
        completed: statsData.completed || 0,
        pending: statsData.pending || 0,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load investigations');
      console.error('Failed to load investigations:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleUpdateStatus = async (id: string, status: string) => {
    try {
      await investigationService.updateStatus(id, status);
      await loadData();
    } catch (err) {
      console.error('Failed to update status:', err);
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-700 rounded w-1/4"></div>
          <div className="grid grid-cols-4 gap-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-24 bg-gray-700 rounded"></div>
            ))}
          </div>
          <div className="space-y-2">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-16 bg-gray-700 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-500/20 border border-red-500 rounded-xl p-4 text-red-400">
          <p>Error: {error}</p>
          <button
            onClick={loadData}
            className="mt-2 px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-white mb-6">Investigation Workspace</h1>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <StatCard label="Total" value={stats.total} color="blue" />
        <StatCard label="Active" value={stats.active} color="green" />
        <StatCard label="Pending" value={stats.pending} color="yellow" />
        <StatCard label="Completed" value={stats.completed} color="gray" />
      </div>

      <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
        <div className="px-4 py-3 border-b border-gray-700">
          <h2 className="text-white font-semibold">Investigations</h2>
        </div>
        {investigations.length === 0 ? (
          <div className="p-8 text-center text-gray-400">No investigations found</div>
        ) : (
          <div className="divide-y divide-gray-700">
            {investigations.map((inv) => (
              <InvestigationItem
                key={inv.id}
                investigation={inv}
                onUpdateStatus={handleUpdateStatus}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function StatCard({ label, value, color }: { label: string; value: number; color: string }) {
  const colors = {
    blue: 'text-blue-400',
    green: 'text-green-400',
    yellow: 'text-yellow-400',
    gray: 'text-gray-400',
    red: 'text-red-400',
  };

  return (
    <div className="bg-gray-800 rounded-xl p-4 border border-gray-700 text-center">
      <p className="text-sm text-gray-400">{label}</p>
      <p className={`text-2xl font-bold ${colors[color as keyof typeof colors]}`}>{value}</p>
    </div>
  );
}

function InvestigationItem({
  investigation,
  onUpdateStatus,
}: {
  investigation: Investigation;
  onUpdateStatus: (id: string, status: string) => void;
}) {
  const statusColors = {
    active: 'bg-green-500/20 text-green-400',
    pending: 'bg-yellow-500/20 text-yellow-400',
    completed: 'bg-gray-500/20 text-gray-400',
    archived: 'bg-gray-500/20 text-gray-500',
  };

  const statusColor = statusColors[investigation.status as keyof typeof statusColors] || statusColors.pending;

  return (
    <div className="px-4 py-3 flex items-center justify-between hover:bg-gray-700/50 transition-colors">
      <div className="flex-1">
        <h3 className="text-white font-medium">{investigation.title}</h3>
        <div className="flex items-center gap-4 mt-1 text-sm text-gray-400">
          <span>Case: {investigation.case_id}</span>
          <span>Priority: {investigation.priority}</span>
          <span>Created: {new Date(investigation.created_at).toLocaleDateString()}</span>
        </div>
      </div>
      <div className="flex items-center gap-3">
        <span className={`px-2 py-1 rounded text-xs font-medium ${statusColor}`}>
          {investigation.status.toUpperCase()}
        </span>
        <select
          value={investigation.status}
          onChange={(e) => onUpdateStatus(investigation.id, e.target.value)}
          className="px-2 py-1 bg-gray-700 border border-gray-600 rounded text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="pending">Pending</option>
          <option value="active">Active</option>
          <option value="completed">Completed</option>
          <option value="archived">Archived</option>
        </select>
      </div>
    </div>
  );
}

// Default export for backward compatibility
export default InvestigationWorkspace;
