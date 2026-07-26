import React, { useState, useEffect } from 'react';
import { alertsApi } from '../../services/api';

interface Alert {
  id: string;
  title: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  status: string;
  created_at: string;
}

interface AlertStats {
  total: number;
  critical: number;
  high: number;
  medium: number;
  low: number;
}

export default function AlertCenter() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [stats, setStats] = useState<AlertStats>({
    total: 0,
    critical: 0,
    high: 0,
    medium: 0,
    low: 0,
  });
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState<{text: string, type: 'success' | 'error' | 'info'} | null>(null);

  const loadAlerts = async () => {
    setLoading(true);
    try {
      const [alertsRes, statsRes] = await Promise.all([
        alertsApi.getAlerts({ limit: 50 }),
        alertsApi.getStats(),
      ]);

      const alertsData = alertsRes?.data || alertsRes || [];
      const statsData = statsRes?.data || statsRes || {};

      setAlerts(Array.isArray(alertsData) ? alertsData : []);
      setStats({
        total: statsData.total || 0,
        critical: statsData.critical || 0,
        high: statsData.high || 0,
        medium: statsData.medium || 0,
        low: statsData.low || 0,
      });
    } catch (error) {
      console.error('Failed to load alerts:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAlerts();
  }, []);

  const handleAction = async (id: string, action: 'acknowledge' | 'resolve' | 'escalate') => {
    try {
      await alertsApi[action](id);
      setMessage({ text: `Alert ${action}d successfully`, type: 'success' });
      setTimeout(() => setMessage(null), 3000);
      await loadAlerts();
    } catch (error: any) {
      if (error.response?.status === 404) {
        // Fallback: update locally
        setAlerts(prev => prev.map(a => 
          a.id === id ? { ...a, status: action === 'acknowledge' ? 'acknowledged' : action === 'resolve' ? 'resolved' : 'escalated' } : a
        ));
        setMessage({ text: `Alert ${action}d locally (backend endpoint not available)`, type: 'info' });
        setTimeout(() => setMessage(null), 3000);
      } else {
        setMessage({ text: `Failed to ${action} alert`, type: 'error' });
        setTimeout(() => setMessage(null), 3000);
      }
    }
  };

  if (loading) {
    return <div className="p-4 text-white">Loading alerts...</div>;
  }

  return (
    <div className="p-4">
      {/* Message Toast */}
      {message && (
        <div className={`mb-4 p-3 rounded-lg ${
          message.type === 'success' ? 'bg-green-500/20 text-green-400 border border-green-500/30' :
          message.type === 'error' ? 'bg-red-500/20 text-red-400 border border-red-500/30' :
          'bg-blue-500/20 text-blue-400 border border-blue-500/30'
        }`}>
          {message.text}
        </div>
      )}

      <div className="grid grid-cols-4 gap-4 mb-6">
        <StatCard label="Total" value={stats.total} color="gray" />
        <StatCard label="Critical" value={stats.critical} color="red" />
        <StatCard label="High" value={stats.high} color="orange" />
        <StatCard label="Medium" value={stats.medium} color="yellow" />
      </div>

      <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-700">
            <tr>
              <th className="px-4 py-2 text-left text-gray-300">Title</th>
              <th className="px-4 py-2 text-left text-gray-300">Severity</th>
              <th className="px-4 py-2 text-left text-gray-300">Status</th>
              <th className="px-4 py-2 text-left text-gray-300">Actions</th>
            </tr>
          </thead>
          <tbody>
            {alerts.length === 0 ? (
              <tr>
                <td colSpan={4} className="px-4 py-4 text-center text-gray-400">
                  No alerts found
                </td>
              </tr>
            ) : (
              alerts.map((alert) => (
                <tr key={alert.id} className="border-t border-gray-700">
                  <td className="px-4 py-2 text-white">{alert.title}</td>
                  <td className="px-4 py-2">
                    <SeverityBadge severity={alert.severity} />
                  </td>
                  <td className="px-4 py-2 text-gray-300">{alert.status}</td>
                  <td className="px-4 py-2">
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleAction(alert.id, 'acknowledge')}
                        className="px-2 py-1 text-xs bg-blue-600 hover:bg-blue-700 rounded disabled:opacity-50"
                        disabled={alert.status === 'acknowledged' || alert.status === 'resolved'}
                      >
                        Acknowledge
                      </button>
                      <button
                        onClick={() => handleAction(alert.id, 'resolve')}
                        className="px-2 py-1 text-xs bg-green-600 hover:bg-green-700 rounded disabled:opacity-50"
                        disabled={alert.status === 'resolved'}
                      >
                        Resolve
                      </button>
                      <button
                        onClick={() => handleAction(alert.id, 'escalate')}
                        className="px-2 py-1 text-xs bg-red-600 hover:bg-red-700 rounded disabled:opacity-50"
                        disabled={alert.status === 'escalated' || alert.status === 'resolved'}
                      >
                        Escalate
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function StatCard({ label, value, color }: { label: string; value: number; color: string }) {
  const colors = {
    gray: 'text-gray-400',
    red: 'text-red-400',
    orange: 'text-orange-400',
    yellow: 'text-yellow-400',
    green: 'text-green-400',
  };

  return (
    <div className="bg-gray-800 rounded-xl p-4 border border-gray-700 text-center">
      <p className="text-sm text-gray-400">{label}</p>
      <p className={`text-2xl font-bold ${colors[color as keyof typeof colors]}`}>{value}</p>
    </div>
  );
}

function SeverityBadge({ severity }: { severity: string }) {
  const colors = {
    critical: 'bg-red-500/20 text-red-400',
    high: 'bg-orange-500/20 text-orange-400',
    medium: 'bg-yellow-500/20 text-yellow-400',
    low: 'bg-green-500/20 text-green-400',
  };

  return (
    <span className={`px-2 py-1 rounded text-xs font-medium ${colors[severity as keyof typeof colors]}`}>
      {severity.toUpperCase()}
    </span>
  );
}
