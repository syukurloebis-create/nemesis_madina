// EvidenceTimeline.tsx - Visual timeline of evidence chain
import React from 'react';
import { CheckCircle, Clock, XCircle, Upload, Shield, RefreshCw, Archive } from 'lucide-react';
import type { Evidence, CustodyRecord } from '../../types';

// Definisikan tipe lokal untuk kompatibilitas
interface CustodyEvent {
  id: string;
  action: 'UPLOAD' | 'VERIFY' | 'REJECT' | 'REVIEW' | 'TRANSFER' | 'ARCHIVE';
  timestamp: string;
  actor?: string;
  notes?: string;
  metadata?: Record<string, any>;
}

type CustodyAction = CustodyEvent['action'];

interface EvidenceTimelineProps {
  events: CustodyEvent[];
  className?: string;
}

const actionConfig: Record<CustodyAction, { label: string; icon: React.ReactNode; color: string }> = {
  UPLOAD: {
    label: 'Uploaded',
    icon: <Upload className="w-4 h-4" />,
    color: 'text-blue-400'
  },
  VERIFY: {
    label: 'Verified',
    icon: <CheckCircle className="w-4 h-4" />,
    color: 'text-green-400'
  },
  REJECT: {
    label: 'Rejected',
    icon: <XCircle className="w-4 h-4" />,
    color: 'text-red-400'
  },
  REVIEW: {
    label: 'In Review',
    icon: <RefreshCw className="w-4 h-4" />,
    color: 'text-yellow-400'
  },
  TRANSFER: {
    label: 'Transferred',
    icon: <Shield className="w-4 h-4" />,
    color: 'text-purple-400'
  },
  ARCHIVE: {
    label: 'Archived',
    icon: <Archive className="w-4 h-4" />,
    color: 'text-gray-400'
  }
};

export const EvidenceTimeline: React.FC<EvidenceTimelineProps> = ({
  events,
  className = ''
}) => {
  if (!events || events.length === 0) {
    return (
      <div className={`text-center text-gray-400 py-4 ${className}`}>
        <Clock className="w-8 h-8 mx-auto mb-2 opacity-50" />
        <p className="text-sm">Belum ada aktivitas custodi</p>
      </div>
    );
  }

  const sortedEvents = [...events].sort((a, b) => 
    new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
  );

  return (
    <div className={`relative ${className}`}>
      <div className="absolute left-3 top-0 bottom-0 w-0.5 bg-dark-border" />
      
      <div className="space-y-4">
        {sortedEvents.map((event, index) => {
          const config = actionConfig[event.action] || actionConfig.UPLOAD;
          const isLast = index === sortedEvents.length - 1;
          
          return (
            <div key={event.id} className="relative pl-10">
              <div className={`absolute left-0 top-1 w-6 h-6 rounded-full flex items-center justify-center bg-dark-card border-2 ${isLast ? 'border-blue-500' : 'border-dark-border'}`}>
                <span className={`${config.color}`}>
                  {config.icon}
                </span>
              </div>
              
              <div className="bg-dark-bg rounded-lg p-3 border border-dark-border">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className={`text-sm font-medium ${config.color}`}>
                      {config.label}
                    </span>
                    <span className="text-xs text-gray-500">
                      by {event.actor || 'System'}
                    </span>
                  </div>
                  <span className="text-xs text-gray-500">
                    {new Date(event.timestamp).toLocaleString('id-ID')}
                  </span>
                </div>
                {event.notes && (
                  <p className="text-xs text-gray-400 mt-1">{event.notes}</p>
                )}
                {event.metadata && (
                  <div className="mt-1 text-xs text-gray-500">
                    {Object.entries(event.metadata).map(([key, value]) => (
                      <span key={key} className="mr-2">
                        {key}: {String(value)}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default EvidenceTimeline;
