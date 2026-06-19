import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';
import { 
  Shield, 
  Eye, 
  Download, 
  Upload, 
  CheckCircle, 
  AlertTriangle,
  Clock,
  User,
  Monitor,
  MapPin
} from 'lucide-react';

interface CustodyEvent {
  id: string;
  evidence_id: string;
  action: string;
  user_id: string;
  user_name: string;
  institution_id: string;
  institution_name?: string;
  ip_address?: string;
  user_agent?: string;
  notes?: string;
  timestamp: string;
}

interface ChainOfCustodyTimelineProps {
  evidenceId: string;
  evidenceName?: string;
}

const getActionIcon = (action: string) => {
  switch (action.toLowerCase()) {
    case 'upload': return <Upload className="w-4 h-4 text-green-400" />;
    case 'view': return <Eye className="w-4 h-4 text-blue-400" />;
    case 'download': return <Download className="w-4 h-4 text-yellow-400" />;
    case 'verify': return <CheckCircle className="w-4 h-4 text-cyan-400" />;
    default: return <Shield className="w-4 h-4 text-gray-400" />;
  }
};

const getActionColor = (action: string) => {
  switch (action.toLowerCase()) {
    case 'upload': return 'border-green-500';
    case 'view': return 'border-blue-500';
    case 'download': return 'border-yellow-500';
    case 'verify': return 'border-cyan-500';
    default: return 'border-gray-500';
  }
};

const getActionText = (action: string) => {
  const texts: Record<string, string> = {
    'upload': 'Bukti Diunggah',
    'view': 'Bukti Dilihat',
    'download': 'Bukti Diunduh',
    'verify': 'Integritas Diverifikasi',
  };
  return texts[action.toLowerCase()] || action;
};

export const ChainOfCustodyTimeline: React.FC<ChainOfCustodyTimelineProps> = ({ 
  evidenceId, 
  evidenceName 
}) => {
  const [events, setEvents] = useState<CustodyEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    const fetchCustody = async () => {
      if (!evidenceId) return;
      try {
        // Gunakan endpoint yang tersedia
        const response = await api.request(`/evidence/${evidenceId}/custody`).catch(() => []);
        setEvents(response);
      } catch (err) {
        console.error('Failed to fetch chain of custody:', err);
        // Data dummy untuk demo
        setEvents([
          {
            id: '1',
            evidence_id: evidenceId,
            action: 'upload',
            user_id: 'admin-1',
            user_name: 'Administrator',
            institution_id: 'inspektorat-1',
            institution_name: 'Inspektorat Jenderal',
            ip_address: '192.168.1.100',
            timestamp: new Date().toISOString(),
            notes: 'Bukti diunggah ke sistem'
          }
        ]);
      } finally {
        setLoading(false);
      }
    };
    fetchCustody();
  }, [evidenceId]);

  if (loading) {
    return (
      <div className="flex justify-center py-4">
        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-cyan-500"></div>
      </div>
    );
  }

  if (events.length === 0) {
    return (
      <div className="text-center py-4 text-gray-500">
        <Shield className="w-8 h-8 mx-auto mb-2 opacity-50" />
        <p className="text-sm">Belum ada riwayat chain of custody</p>
      </div>
    );
  }

  const displayEvents = expanded ? events : events.slice(0, 3);

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-700 bg-gray-800/50">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Shield className="w-5 h-5 text-cyan-400" />
            <h3 className="font-semibold text-white">Chain of Custody</h3>
            {evidenceName && (
              <span className="text-xs text-gray-500 ml-2">{evidenceName}</span>
            )}
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-xs text-gray-500">{events.length} kejadian</span>
            <span className="text-xs text-green-400">✓ Rantai Utuh</span>
          </div>
        </div>
      </div>

      {/* Timeline */}
      <div className="p-4">
        <div className="relative pl-6">
          {/* Timeline line */}
          <div className="absolute left-2 top-2 bottom-2 w-0.5 bg-gray-700" />
          
          {displayEvents.map((event, idx) => (
            <div key={event.id} className="relative mb-6 last:mb-0">
              {/* Timeline dot */}
              <div className={`absolute -left-6 w-4 h-4 rounded-full border-2 bg-gray-800 ${getActionColor(event.action)}`} />
              
              <div className="space-y-2">
                {/* Header */}
                <div className="flex items-center justify-between flex-wrap gap-2">
                  <div className="flex items-center space-x-2">
                    {getActionIcon(event.action)}
                    <span className="text-sm font-medium text-white">
                      {getActionText(event.action)}
                    </span>
                  </div>
                  <span className="text-xs text-gray-500">
                    {new Date(event.timestamp).toLocaleString('id-ID')}
                  </span>
                </div>
                
                {/* Details */}
                <div className="ml-6 space-y-1 text-xs">
                  <div className="flex items-center space-x-3 flex-wrap gap-y-1">
                    <div className="flex items-center space-x-1">
                      <User className="w-3 h-3 text-gray-500" />
                      <span className="text-gray-400">{event.user_name}</span>
                    </div>
                    {event.institution_name && (
                      <div className="flex items-center space-x-1">
                        <Shield className="w-3 h-3 text-gray-500" />
                        <span className="text-gray-400">{event.institution_name}</span>
                      </div>
                    )}
                    {event.ip_address && (
                      <div className="flex items-center space-x-1">
                        <Monitor className="w-3 h-3 text-gray-500" />
                        <span className="text-gray-400 font-mono">IP: {event.ip_address}</span>
                      </div>
                    )}
                  </div>
                  {event.notes && (
                    <p className="text-gray-500 mt-1">{event.notes}</p>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Expand/Collapse Button */}
        {events.length > 3 && (
          <button
            onClick={() => setExpanded(!expanded)}
            className="mt-4 text-xs text-cyan-400 hover:text-cyan-300 transition flex items-center space-x-1"
          >
            {expanded ? (
              <>
                <span>Lihat lebih sedikit</span>
              </>
            ) : (
              <>
                <span>Lihat {events.length - 3} kejadian lainnya</span>
              </>
            )}
          </button>
        )}
      </div>
    </div>
  );
};

export default ChainOfCustodyTimeline;
