import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';
import { 
  History, 
  Filter, 
  Download, 
  Search,
  User,
  Monitor,
  Calendar,
  FileText,
  AlertTriangle,
  CheckCircle,
  Eye,
  Edit,
  Trash2,
  Upload,
  Shield
} from 'lucide-react';

interface AuditLog {
  id: string;
  action: string;
  user_id: string;
  user_name: string;
  user_email?: string;
  institution_id: string;
  institution_name?: string;
  target_type: string;
  target_id: string;
  target_name?: string;
  details: Record<string, any>;
  ip_address?: string;
  user_agent?: string;
  timestamp: string;
}

interface AuditTrailEnhancedProps {
  limit?: number;
  caseId?: string;
  entityId?: string;
}

const getActionIcon = (action: string) => {
  const icons: Record<string, JSX.Element> = {
    'CREATE': <FileText className="w-4 h-4 text-green-400" />,
    'UPDATE': <Edit className="w-4 h-4 text-blue-400" />,
    'DELETE': <Trash2 className="w-4 h-4 text-red-400" />,
    'VIEW': <Eye className="w-4 h-4 text-gray-400" />,
    'UPLOAD': <Upload className="w-4 h-4 text-cyan-400" />,
    'VERIFY': <Shield className="w-4 h-4 text-purple-400" />,
  };
  return icons[action] || <History className="w-4 h-4 text-gray-400" />;
};

const getActionBadge = (action: string) => {
  const badges: Record<string, string> = {
    'CREATE': 'bg-green-900 text-green-300',
    'UPDATE': 'bg-blue-900 text-blue-300',
    'DELETE': 'bg-red-900 text-red-300',
    'VIEW': 'bg-gray-700 text-gray-300',
    'UPLOAD': 'bg-cyan-900 text-cyan-300',
    'VERIFY': 'bg-purple-900 text-purple-300',
  };
  return badges[action] || 'bg-gray-700 text-gray-300';
};

export const AuditTrailEnhanced: React.FC<AuditTrailEnhancedProps> = ({ 
  limit = 50, 
  caseId, 
  entityId 
}) => {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('');
  const [actionFilter, setActionFilter] = useState<string>('all');
  const [dateFilter, setDateFilter] = useState<string>('all');

  useEffect(() => {
    const fetchAuditLogs = async () => {
      try {
        let url = '/audit/logs';
        const params = new URLSearchParams();
        params.append('limit', limit.toString());
        if (caseId) params.append('case_id', caseId);
        if (entityId) params.append('entity_id', entityId);
        
        const response = await api.request(`${url}?${params.toString()}`).catch(() => []);
        
        // Data dummy untuk demo
        const dummyLogs: AuditLog[] = [
          {
            id: '1',
            action: 'CREATE',
            user_id: 'admin-1',
            user_name: 'Administrator',
            institution_id: 'inspektorat-1',
            institution_name: 'Inspektorat Jenderal',
            target_type: 'case',
            target_id: caseId || 'case-001',
            target_name: 'Kasus Korupsi Proyek',
            details: { title: 'Kasus Korupsi Proyek', priority: 'HIGH' },
            ip_address: '192.168.1.100',
            timestamp: new Date().toISOString()
          },
          {
            id: '2',
            action: 'UPDATE',
            user_id: 'investigator-1',
            user_name: 'Penyidik',
            institution_id: 'kpk-1',
            institution_name: 'KPK',
            target_type: 'case',
            target_id: caseId || 'case-001',
            target_name: 'Kasus Korupsi Proyek',
            details: { status: 'INVESTIGATING', assigned_to: 'investigator-1' },
            ip_address: '192.168.1.101',
            timestamp: new Date(Date.now() - 3600000).toISOString()
          }
        ];
        setLogs(response.length ? response : dummyLogs);
      } catch (err) {
        console.error('Failed to fetch audit logs:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchAuditLogs();
  }, [limit, caseId, entityId]);

  const filteredLogs = logs.filter(log => {
    const matchesAction = actionFilter === 'all' || log.action === actionFilter;
    const matchesSearch = filter === '' || 
      log.user_name.toLowerCase().includes(filter.toLowerCase()) ||
      log.target_name?.toLowerCase().includes(filter.toLowerCase()) ||
      log.details?.title?.toLowerCase().includes(filter.toLowerCase());
    
    let matchesDate = true;
    if (dateFilter !== 'all') {
      const logDate = new Date(log.timestamp);
      const now = new Date();
      const days = parseInt(dateFilter);
      const diffDays = (now.getTime() - logDate.getTime()) / (1000 * 3600 * 24);
      matchesDate = diffDays <= days;
    }
    
    return matchesAction && matchesSearch && matchesDate;
  });

  const exportToCSV = () => {
    const headers = ['Waktu', 'Aksi', 'Pengguna', 'Instansi', 'Target', 'Detail', 'IP'];
    const rows = filteredLogs.map(log => [
      new Date(log.timestamp).toLocaleString('id-ID'),
      log.action,
      log.user_name,
      log.institution_name || log.institution_id,
      log.target_name || log.target_id,
      JSON.stringify(log.details),
      log.ip_address || '-'
    ]);
    
    const csvContent = [headers, ...rows].map(row => row.join(',')).join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `audit_log_${new Date().toISOString().slice(0, 19)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const actionOptions = [
    { value: 'all', label: 'Semua Aksi' },
    { value: 'CREATE', label: 'Membuat' },
    { value: 'UPDATE', label: 'Mengubah' },
    { value: 'DELETE', label: 'Menghapus' },
    { value: 'VIEW', label: 'Melihat' },
    { value: 'UPLOAD', label: 'Mengunggah' },
    { value: 'VERIFY', label: 'Memverifikasi' },
  ];

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-700 flex justify-between items-center flex-wrap gap-3">
        <div className="flex items-center space-x-2">
          <History className="w-5 h-5 text-cyan-400" />
          <h3 className="font-semibold text-white">Jejak Audit</h3>
          <span className="text-xs text-gray-500">{logs.length} kejadian</span>
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={exportToCSV}
            className="px-3 py-1 text-xs bg-gray-700 text-gray-300 rounded hover:bg-gray-600 transition flex items-center space-x-1"
          >
            <Download className="w-3 h-3" />
            <span>Ekspor CSV</span>
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="px-4 py-3 border-b border-gray-700 bg-gray-800/50">
        <div className="flex flex-wrap gap-3">
          <div className="flex-1 min-w-[200px]">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-3 h-3 text-gray-500" />
              <input
                type="text"
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                placeholder="Cari pengguna, target, atau detail..."
                className="w-full bg-gray-700 border border-gray-600 rounded-lg py-1.5 pl-8 pr-3 text-sm text-white placeholder-gray-400"
              />
            </div>
          </div>
          
          <select
            value={actionFilter}
            onChange={(e) => setActionFilter(e.target.value)}
            className="bg-gray-700 border border-gray-600 rounded-lg px-3 py-1.5 text-sm text-white"
          >
            {actionOptions.map(opt => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
          
          <select
            value={dateFilter}
            onChange={(e) => setDateFilter(e.target.value)}
            className="bg-gray-700 border border-gray-600 rounded-lg px-3 py-1.5 text-sm text-white"
          >
            <option value="all">Semua Waktu</option>
            <option value="1">24 Jam Terakhir</option>
            <option value="7">7 Hari Terakhir</option>
            <option value="30">30 Hari Terakhir</option>
          </select>
        </div>
      </div>

      {/* Audit Logs List */}
      {loading ? (
        <div className="flex justify-center py-8">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-cyan-500"></div>
        </div>
      ) : filteredLogs.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <History className="w-12 h-12 mx-auto mb-2 opacity-50" />
          <p>Tidak ada jejak audit ditemukan</p>
        </div>
      ) : (
        <div className="divide-y divide-gray-700 max-h-96 overflow-y-auto">
          {filteredLogs.map((log) => (
            <div key={log.id} className="p-4 hover:bg-gray-700/30 transition">
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3">
                  {getActionIcon(log.action)}
                  <div>
                    <div className="flex items-center space-x-2 flex-wrap gap-y-1">
                      <span className={`text-xs px-2 py-0.5 rounded ${getActionBadge(log.action)}`}>
                        {log.action}
                      </span>
                      <span className="text-sm text-white">
                        {log.target_name || log.target_id}
                      </span>
                      <span className="text-xs text-gray-500 capitalize">
                        {log.target_type}
                      </span>
                    </div>
                    <div className="mt-1 flex items-center space-x-3 text-xs text-gray-500">
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
                      {log.ip_address && (
                        <div className="flex items-center space-x-1">
                          <Monitor className="w-3 h-3" />
                          <span>{log.ip_address}</span>
                        </div>
                      )}
                      <div className="flex items-center space-x-1">
                        <Calendar className="w-3 h-3" />
                        <span>{new Date(log.timestamp).toLocaleString('id-ID')}</span>
                      </div>
                    </div>
                    {Object.keys(log.details).length > 0 && (
                      <div className="mt-2 text-xs text-gray-600 font-mono">
                        {JSON.stringify(log.details).substring(0, 100)}
                        {JSON.stringify(log.details).length > 100 ? '...' : ''}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
