import React, { useEffect, useState } from 'react';
import { useAuthStore } from '../../stores/authStore';

interface AuditLog {
  id: string;
  action: string;
  entity_type: string;
  entity_id: string;
  user_id: string;
  user_name: string;
  changes: Record<string, any>;
  timestamp: string;
  ip_address?: string;
}

const AuditTrail: React.FC<{ entityId?: string; entityType?: string }> = ({ entityId, entityType }) => {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('');
  const { token } = useAuthStore();

  useEffect(() => {
    fetchAuditLogs();
  }, [entityId, entityType]);

  const fetchAuditLogs = async () => {
    try {
      setLoading(true);
      let url = 'http://localhost/audit/logs';
      if (entityId && entityType) {
        url += `?entity_id=${entityId}&entity_type=${entityType}`;
      }
      const response = await fetch(url, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setLogs(data.data || data || []);
      } else {
        // Mock data for demo
        setLogs([
          {
            id: '1',
            action: 'CASE_CREATED',
            entity_type: 'case',
            entity_id: 'case-001',
            user_id: 'user-001',
            user_name: 'Admin User',
            changes: { title: 'Fraud Investigation', priority: 'HIGH' },
            timestamp: new Date().toISOString(),
          },
          {
            id: '2',
            action: 'EVIDENCE_ADDED',
            entity_type: 'evidence',
            entity_id: 'evid-001',
            user_id: 'user-001',
            user_name: 'Admin User',
            changes: { title: 'Financial Report', type: 'document' },
            timestamp: new Date(Date.now() - 3600000).toISOString(),
          },
          {
            id: '3',
            action: 'CASE_ASSIGNED',
            entity_type: 'case',
            entity_id: 'case-001',
            user_id: 'user-002',
            user_name: 'Investigator',
            changes: { assignee: 'investigator_01', status: 'INVESTIGATING' },
            timestamp: new Date(Date.now() - 7200000).toISOString(),
          },
        ]);
      }
    } catch (error) {
      console.error('Failed to fetch audit logs:', error);
    } finally {
      setLoading(false);
    }
  };

  const getActionIcon = (action: string) => {
    const icons: Record<string, string> = {
      CASE_CREATED: '📋',
      CASE_ASSIGNED: '👤',
      CASE_UPDATED: '✏️',
      CASE_CLOSED: '🔒',
      EVIDENCE_ADDED: '📎',
      EVIDENCE_UPDATED: '✏️',
      STATUS_CHANGED: '🔄',
      USER_LOGIN: '🔐',
      USER_LOGOUT: '🚪',
    };
    return icons[action] || '📌';
  };

  const getActionColor = (action: string) => {
    if (action.includes('CREATED')) return 'text-green-400';
    if (action.includes('UPDATED')) return 'text-yellow-400';
    if (action.includes('DELETED')) return 'text-red-400';
    if (action.includes('ASSIGNED')) return 'text-blue-400';
    return 'text-gray-400';
  };

  const filteredLogs = logs.filter(log =>
    log.action.toLowerCase().includes(filter.toLowerCase()) ||
    log.user_name.toLowerCase().includes(filter.toLowerCase()) ||
    log.entity_type.toLowerCase().includes(filter.toLowerCase())
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Filter */}
      <div className="flex gap-4">
        <input
          type="text"
          placeholder="Filter by action, user, or entity..."
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="flex-1 px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-green-500"
        />
      </div>

      {/* Audit Trail Timeline */}
      <div className="space-y-4">
        {filteredLogs.length === 0 ? (
          <div className="text-center py-12 text-gray-500">No audit logs found</div>
        ) : (
          filteredLogs.map((log, idx) => (
            <div key={log.id} className="relative pl-8 pb-6">
              {/* Timeline line */}
              {idx < filteredLogs.length - 1 && (
                <div className="absolute left-3 top-6 bottom-0 w-0.5 bg-gray-700"></div>
              )}
              {/* Timeline dot */}
              <div className="absolute left-0 top-1 w-6 h-6 rounded-full bg-gray-700 flex items-center justify-center">
                <span className="text-sm">{getActionIcon(log.action)}</span>
              </div>
              {/* Content */}
              <div className="bg-gray-700/30 rounded-lg p-4">
                <div className="flex justify-between items-start">
                  <div>
                    <h4 className={`font-semibold ${getActionColor(log.action)}`}>
                      {log.action.replace(/_/g, ' ')}
                    </h4>
                    <p className="text-sm text-gray-400 mt-1">
                      <span className="font-medium text-gray-300">{log.user_name}</span>
                      {' '}on{' '}
                      <span className="font-medium text-gray-300">{log.entity_type}</span>
                      {' '}<span className="font-mono text-xs">{log.entity_id.slice(0, 8)}...</span>
                    </p>
                    {Object.keys(log.changes).length > 0 && (
                      <div className="mt-2 text-xs text-gray-500 bg-gray-800/50 rounded p-2">
                        {Object.entries(log.changes).map(([key, value]) => (
                          <div key={key} className="flex gap-2">
                            <span className="text-gray-400">{key}:</span>
                            <span className="text-gray-300">{String(value)}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-gray-500">
                      {new Date(log.timestamp).toLocaleString()}
                    </p>
                    {log.ip_address && (
                      <p className="text-xs text-gray-600 mt-1">{log.ip_address}</p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default AuditTrail;
