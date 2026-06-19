// src/components/entity/GovernanceHistory.tsx
import React from 'react';

interface AuditEvent {
  id: string;
  timestamp: string;
  action: string;
  user: string;
  details: Record<string, any>;
  case_id?: string;
}

interface GovernanceHistoryProps {
  entityId: string;
}

const mockAuditEvents: AuditEvent[] = [
  { id: '1', timestamp: '2026-06-01T10:00:00', action: 'ENTITY_CREATED', user: 'system', details: { source: 'API' } },
  { id: '2', timestamp: '2026-06-02T14:30:00', action: 'RISK_SCORE_UPDATED', user: 'auditor@inspektorat.go.id', details: { old_score: 45, new_score: 68 }, case_id: 'CASE-001' },
  { id: '3', timestamp: '2026-06-03T09:15:00', action: 'RELATIONSHIP_ADDED', user: 'investigator@kpk.go.id', details: { target: 'VENDOR-002', type: 'collusion' }, case_id: 'CASE-002' },
  { id: '4', timestamp: '2026-06-05T16:45:00', action: 'CASE_LINKED', user: 'auditor@bpkp.go.id', details: { case_id: 'CASE-003' }, case_id: 'CASE-003' },
  { id: '5', timestamp: '2026-06-07T11:00:00', action: 'FLAG_REVIEW', user: 'system', details: { reason: 'High risk detected' } },
];

export const GovernanceHistory: React.FC<GovernanceHistoryProps> = ({ entityId }) => {
  const getActionIcon = (action: string) => {
    switch (action) {
      case 'ENTITY_CREATED': return '➕';
      case 'RISK_SCORE_UPDATED': return '📊';
      case 'RELATIONSHIP_ADDED': return '🔗';
      case 'CASE_LINKED': return '📁';
      case 'FLAG_REVIEW': return '🚩';
      default: return '📝';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-4 border-b">
        <h3 className="text-lg font-medium text-gray-900">Governance History</h3>
        <p className="text-sm text-gray-500 mt-1">Audit trail for entity {entityId}</p>
      </div>
      <div className="divide-y max-h-96 overflow-y-auto">
        {mockAuditEvents.map((event) => (
          <div key={event.id} className="p-4 hover:bg-gray-50">
            <div className="flex items-start gap-3">
              <span className="text-xl">{getActionIcon(event.action)}</span>
              <div className="flex-1">
                <div className="flex justify-between items-start">
                  <div>
                    <p className="font-medium text-gray-900">{event.action}</p>
                    <p className="text-sm text-gray-500 mt-1">
                      By: {event.user}
                      {event.case_id && <span className="ml-2 text-blue-600">Case: {event.case_id}</span>}
                    </p>
                  </div>
                  <span className="text-xs text-gray-400">
                    {new Date(event.timestamp).toLocaleString()}
                  </span>
                </div>
                {Object.keys(event.details).length > 0 && (
                  <div className="mt-2 text-xs text-gray-500 bg-gray-50 p-2 rounded">
                    {Object.entries(event.details).map(([key, val]) => (
                      <span key={key} className="mr-3">
                        {key}: {String(val)}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
