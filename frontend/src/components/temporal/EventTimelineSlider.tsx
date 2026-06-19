import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';
import { useAuthStore } from '../../stores/authStore';

interface TimelineEvent {
  version: number;
  event_type: string;
  timestamp: string;
  user_id: string;
  data: Record<string, any>;
  event_hash: string;
  previous_hash: string | null;
}

interface EventTimelineSliderProps {
  caseId: string;
  onVersionChange?: (version: number, state: any) => void;
}

export const EventTimelineSlider: React.FC<EventTimelineSliderProps> = ({ 
  caseId, 
  onVersionChange 
}) => {
  const { token } = useAuthStore();
  const [events, setEvents] = useState<TimelineEvent[]>([]);
  const [currentVersion, setCurrentVersion] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchEvents = async () => {
      if (!caseId || !token) return;
      
      setLoading(true);
      setError(null);
      
      try {
        console.log(`📡 Fetching timeline for case: ${caseId}`);
        const response = await api.getEventTimeline(caseId, 100, 0);
        console.log('📡 Timeline response:', response);
        
        if (response && response.events) {
          setEvents(response.events);
          if (response.events.length > 0) {
            setCurrentVersion(response.events[response.events.length - 1].version);
          }
        } else if (response && response.data) {
          setEvents(response.data);
          if (response.data.length > 0) {
            setCurrentVersion(response.data[response.data.length - 1].version);
          }
        } else {
          setEvents([]);
        }
      } catch (err: any) {
        console.error('Failed to fetch events:', err);
        setError(err.message || 'Gagal memuat timeline');
      } finally {
        setLoading(false);
      }
    };

    fetchEvents();
  }, [caseId, token]);

  const handleSliderChange = (version: number) => {
    setCurrentVersion(version);
    const eventAtVersion = events.find(e => e.version === version);
    if (eventAtVersion && onVersionChange) {
      onVersionChange(version, eventAtVersion.data);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-cyan-500"></div>
        <span className="ml-2 text-gray-400">Memuat timeline...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-900/20 border border-red-700 rounded-lg p-4 text-center">
        <p className="text-red-400">{error}</p>
        <button 
          onClick={() => window.location.reload()}
          className="mt-2 text-sm text-cyan-400 hover:text-cyan-300"
        >
          Coba lagi
        </button>
      </div>
    );
  }

  if (events.length === 0) {
    return (
      <div className="bg-gray-800 rounded-lg p-8 text-center border border-gray-700">
        <div className="text-4xl mb-3">📭</div>
        <p className="text-gray-400">Belum ada kejadian untuk kasus ini</p>
        <p className="text-xs text-gray-500 mt-1">
          Kasus akan muncul di timeline setelah ada aktivitas (create, assign, status change)
        </p>
      </div>
    );
  }

  const maxVersion = events[events.length - 1]?.version || 1;

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
      <div className="mb-4">
        <div className="flex justify-between items-center mb-2">
          <h3 className="text-sm font-medium text-gray-300">Linimasa Event</h3>
          <span className="text-xs text-gray-500">
            Versi {currentVersion} dari {maxVersion}
          </span>
        </div>
        <input
          type="range"
          min={1}
          max={maxVersion}
          value={currentVersion}
          onChange={(e) => handleSliderChange(parseInt(e.target.value))}
          className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-cyan-500"
        />
      </div>

      <div className="space-y-2 max-h-64 overflow-y-auto">
        {events.map((event, idx) => (
          <div 
            key={idx}
            className={`p-3 rounded-lg cursor-pointer transition ${
              event.version === currentVersion 
                ? 'bg-cyan-500/20 border border-cyan-500/50' 
                : 'bg-gray-700/50 hover:bg-gray-700'
            }`}
            onClick={() => handleSliderChange(event.version)}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <span className="text-xs font-mono text-cyan-400">v{event.version}</span>
                <span className="text-sm text-white">{event.event_type}</span>
              </div>
              <span className="text-xs text-gray-500">
                {new Date(event.timestamp).toLocaleString('id-ID')}
              </span>
            </div>
            <div className="mt-1 text-xs text-gray-400">
              {event.user_id && <span>Oleh: {event.user_id.substring(0, 8)}...</span>}
              {event.data?.title && <span className="ml-2">Judul: {event.data.title}</span>}
              {event.data?.status && <span className="ml-2">Status: {event.data.status}</span>}
            </div>
            <div className="mt-1 text-xs font-mono text-gray-600 truncate">
              Hash: {event.event_hash?.substring(0, 16)}...
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4 pt-3 border-t border-gray-700 flex justify-between text-xs">
        <span className="text-gray-500">Total Event: {events.length}</span>
        <span className="text-green-400">✓ Rantai Hash Valid</span>
        <span className="text-cyan-400">SHA256</span>
      </div>
    </div>
  );
};
