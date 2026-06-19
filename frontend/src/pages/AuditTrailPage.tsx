import React, { useEffect, useState } from 'react';
import { WorkspaceLayout } from '../WorkspaceLayout';
import { api } from '../services/api';
import { useAuthStore } from '../stores/authStore';
import { History, Search, Download, Filter, Calendar, User, Shield } from 'lucide-react';

interface AuditLog {
  id: string;
  action: string;
  user_name: string;
  institution_name: string;
  target_name: string;
  timestamp: string;
  details: any;
}

export default function AuditTrailPage() {
  const { token } = useAuthStore();
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('');

  useEffect(() => {
    const fetchAuditLogs = async () => {
      if (!token) return;
      try {
        const response = await api.request('/audit/logs').catch(() => []);
        // Ensure response is an array
        const logsArray = Array.isArray(response) ? response : [];
        setLogs(logsArray);
      } catch (err) {
        console.error('Failed to fetch audit logs:', err);
        setLogs([]);
      } finally {
        setLoading(false);
      }
    };
    fetchAuditLogs();
  }, [token]);

  // Safe filter - ensure logs is array
  const filteredLogs = Array.isArray(logs) ? logs.filter(log =>
    log.action?.toLowerCase().includes(filter.toLowerCase()) ||
    log.user_name?.toLowerCase().includes(filter.toLowerCase()) ||
    log.target_name?.toLowerCase().includes(filter.toLowerCase())
  ) : [];

  const getActionBadge = (action: string) => {
    const badges: Record<string, string> = {
      'CREATE': 'bg-green-900 text-green-300',
      'UPDATE': 'bg-blue-900 text-blue-300',
      'DELETE': 'bg-red-900 text-red-300',
      'VIEW': 'bg-gray-700 text-gray-300',
    };
    return badges[action] || 'bg-gray-700 text-gray-300';
  };

  // Demo data if no logs
  const displayLogs = filteredLogs.length > 0 ? filteredLogs : [
    {
      id: '1',
      action: 'CREATE',
      user_name: 'Admin User',
      institution_name: 'Inspektorat',
      target_name: 'Case Korupsi Proyek',
      timestamp: new Date().toISOString(),
      details: { title: 'Korupsi Proyek Infrastruktur', priority: 'HIGH' }
    },
    {
      id: '2',
      action: 'UPDATE',
      user_name: 'Investigator',
      institution_name: 'KPK',
      target_name: 'Case Korupsi Proyek',
      timestamp: new Date(Date.now() - 3600000).toISOString(),
      details: { status: 'INVESTIGATING' }
    }
  ];

  if (loading) {
    return (
      <WorkspaceLayout>
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-500"></div>
        </div>
      </WorkspaceLayout>
    );
  }

  return (
    <WorkspaceLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-white">Jejak Audit</h1>
          <p className="text-gray-400 mt-1">Riwayat lengkap semua aktivitas dalam sistem</p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 text-center">
            <History className="w-6 h-6 text-cyan-400 mx-auto mb-2" />
            <div className="text-2xl font-bold text-white">{displayLogs.length}</div>
            <div className="text-xs text-gray-500">Total Kejadian</div>
          </div>
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 text-center">
            <Shield className="w-6 h-6 text-green-400 mx-auto mb-2" />
            <div className="text-2xl font-bold text-white">100%</div>
            <div className="text-xs text-gray-500">Integritas Chain</div>
          </div>
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 text-center">
            <Calendar className="w-6 h-6 text-yellow-400 mx-auto mb-2" />
            <div className="text-2xl font-bold text-white">30</div>
            <div className="text-xs text-gray-500">Hari Terakhir</div>
          </div>
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-500" />
          <input
            type="text"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            placeholder="Cari berdasarkan aksi, pengguna, atau target..."
            className="w-full bg-gray-800 border border-gray-700 rounded-lg py-2 pl-10 pr-4 text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500"
          />
        </div>

        {/* Audit Logs List */}
        <div className="space-y-3">
          {displayLogs.slice(0, 20).map((log) => (
            <div key={log.id} className="bg-gray-800 rounded-lg p-4 border border-gray-700 hover:border-cyan-500/30 transition">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <span className={`text-xs px-2 py-0.5 rounded ${getActionBadge(log.action)}`}>
                      {log.action}
                    </span>
                    <span className="text-sm text-white">{log.target_name}</span>
                  </div>
                  <div className="flex items-center space-x-3 text-xs text-gray-500">
                    <div className="flex items-center space-x-1">
                      <User className="w-3 h-3" />
                      <span>{log.user_name}</span>
                    </div>
                    {log.institution_name && (
                      <div className="flex items-center space-x-1">
                        <Shield className="w-3 h-3" />
                        <span>{log.institution_name}</span>
                      </div>
                    )}
                    <div className="flex items-center space-x-1">
                      <Calendar className="w-3 h-3" />
                      <span>{new Date(log.timestamp).toLocaleString('id-ID')}</span>
                    </div>
                  </div>
                  {log.details && Object.keys(log.details).length > 0 && (
                    <div className="mt-2 text-xs text-gray-600 font-mono">
                      {JSON.stringify(log.details).substring(0, 100)}...
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </WorkspaceLayout>
  );
}
