import React, { useEffect, useState } from 'react';
import { useAuthStore } from '../../stores/authStore';
import { api } from '../../services/api';

interface TimelineEvent {
  version: number;
  event_type: string;
  timestamp: string;
  user_id: string;
  data: Record<string, any>;
  event_hash?: string;
  previous_hash?: string;
}

interface ForensicTimelineProps {
  caseId: string;
}

const ForensicTimeline: React.FC<ForensicTimelineProps> = ({ caseId }) => {
  const [events, setEvents] = useState<TimelineEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { token } = useAuthStore();

  useEffect(() => {
    if (caseId && token) {
      fetchTimeline();
    }
  }, [caseId, token]);

  const fetchTimeline = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.getCaseTimeline(caseId);
      
      // Extract timeline array
      let timeline: TimelineEvent[] = [];
      if (Array.isArray(data)) {
        timeline = data;
      } else if (data?.timeline && Array.isArray(data.timeline)) {
        timeline = data.timeline;
      } else {
        timeline = [];
      }
      
      setEvents(timeline);
    } catch (error) {
      console.error('Failed to fetch timeline:', error);
      setError('Gagal memuat garis waktu forensik');
    } finally {
      setLoading(false);
    }
  };

  const getEventIcon = (eventType: string) => {
    const icons: Record<string, string> = {
      case_created: '📋',
      case_assigned: '👤',
      evidence_added: '📎',
      status_changed: '🔄',
      case_closed: '🔒'
    };
    return icons[eventType] || '📌';
  };

  const getEventColor = (eventType: string) => {
    const colors: Record<string, string> = {
      case_created: 'border-green-500',
      case_assigned: 'border-blue-500',
      evidence_added: 'border-yellow-500',
      status_changed: 'border-purple-500',
      case_closed: 'border-gray-500'
    };
    return colors[eventType] || 'border-gray-500';
  };

  if (loading) {
    return (
      <div className="text-center py-8 text-gray-400">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-500 mx-auto mb-2"></div>
        Memuat garis waktu...
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8 text-red-400">
        <p>{error}</p>
        <button onClick={fetchTimeline} className="mt-2 text-sm text-blue-400 hover:text-blue-300">
          Coba Lagi
        </button>
      </div>
    );
  }

  if (events.length === 0) {
    return <div className="text-center py-8 text-gray-500">Tidak ada kejadian ditemukan untuk kasus ini</div>;
  }

  return (
    <div className="relative pl-4">
      <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-700"></div>
      {events.map((event, idx) => (
        <div key={idx} className="relative flex items-start mb-6">
          <div className={`absolute -left-2 w-4 h-4 rounded-full border-2 border-gray-800 ${getEventColor(event.event_type)}`}></div>
          <div className="ml-8 flex-1">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xl">{getEventIcon(event.event_type)}</span>
              <span className="font-semibold text-white">
                {event.event_type?.replace(/_/g, ' ').toUpperCase() || 'KEJADIAN'}
              </span>
              <span className="text-xs text-gray-500">v{event.version}</span>
            </div>
            <div className="text-sm text-gray-400">
              {event.timestamp ? new Date(event.timestamp).toLocaleString() : '-'}
            </div>
            {event.event_hash && (
              <div className="mt-1 text-xs font-mono text-gray-500">
                Hash: {event.event_hash.slice(0, 16)}...
              </div>
            )}
            {event.data && Object.keys(event.data).length > 0 && (
              <div className="mt-1 text-xs text-gray-500 bg-gray-800/50 rounded p-2">
                {event.data.assignee && <span>👤 Ditugaskan ke: {event.data.assignee}</span>}
                {event.data.title && !event.data.assignee && <span>📝 {event.data.title}</span>}
                {event.data.evidence_id && <span>📎 Bukti: {event.data.evidence_id}</span>}
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

export default ForensicTimeline;
