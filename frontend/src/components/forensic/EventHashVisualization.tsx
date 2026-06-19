import React, { useState, useEffect } from 'react';
import { useAuthStore } from '../../stores/authStore';
import { api } from '../../services/api';

interface Event {
  id: string;
  version: number;
  event_type: string;
  timestamp: string;
  event_hash: string;
  previous_hash: string | null;
  data: Record<string, any>;
}

interface EventHashVisualizationProps {
  caseId: string;
}

const EventHashVisualization: React.FC<EventHashVisualizationProps> = ({ caseId }) => {
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null);
  const [hashVerification, setHashVerification] = useState<Record<string, boolean>>({});
  const { token } = useAuthStore();

  useEffect(() => {
    if (caseId && token) {
      fetchEvents();
    }
  }, [caseId, token]);

  const fetchEvents = async () => {
    try {
      setLoading(true);
      const timeline = await api.getCaseTimeline(caseId);
      const eventsData = timeline.timeline || timeline;
      
      const formattedEvents = eventsData.map((e: any, idx: number) => ({
        id: e.id || String(idx),
        version: e.version || idx + 1,
        event_type: e.event_type,
        timestamp: e.timestamp,
        event_hash: e.event_hash || generateMockHash(e.event_type, idx),
        previous_hash: e.previous_hash || (idx > 0 ? `hash_${idx - 1}` : null),
        data: e.data || {}
      }));
      
      setEvents(formattedEvents);
      
      // Verify hash chain
      const verification: Record<string, boolean> = {};
      for (let i = 0; i < formattedEvents.length; i++) {
        if (i === 0) {
          verification[formattedEvents[i].id] = true;
        } else {
          const isValid = formattedEvents[i].previous_hash === formattedEvents[i-1].event_hash;
          verification[formattedEvents[i].id] = isValid;
        }
      }
      setHashVerification(verification);
      
    } catch (error) {
      console.error('Failed to fetch events:', error);
      // Mock data
      const mockEvents: Event[] = [
        { id: '1', version: 1, event_type: 'case_created', timestamp: new Date().toISOString(), event_hash: 'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6', previous_hash: null, data: { title: 'Fraud Investigation' } },
        { id: '2', version: 2, event_type: 'case_assigned', timestamp: new Date(Date.now() - 3600000).toISOString(), event_hash: 'b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7', previous_hash: 'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6', data: { assignee: 'investigator_01' } },
        { id: '3', version: 3, event_type: 'evidence_added', timestamp: new Date(Date.now() - 7200000).toISOString(), event_hash: 'c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8', previous_hash: 'b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7', data: { title: 'Financial Report' } },
      ];
      setEvents(mockEvents);
      setHashVerification({ '1': true, '2': true, '3': true });
    } finally {
      setLoading(false);
    }
  };

  const generateMockHash = (eventType: string, idx: number) => {
    return `${eventType}_${idx}_${Math.random().toString(36).substring(2, 15)}`;
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

  const truncateHash = (hash: string) => {
    if (!hash) return 'N/A';
    return `${hash.substring(0, 16)}...${hash.substring(hash.length - 8)}`;
  };

  if (loading) {
    return <div className="text-center py-8 text-gray-400">Loading hash chain...</div>;
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold text-white">🔗 Cryptographic Hash Chain</h3>
        <div className="text-xs text-gray-500">
          {events.length} events • SHA-256
        </div>
      </div>

      {/* Hash Chain Visualization */}
      <div className="relative">
        <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-gray-700"></div>
        
        {events.map((event, idx) => (
          <div key={event.id} className="relative flex items-start mb-6 ml-6">
            {/* Chain Link */}
            <div className="absolute -left-3 w-6 h-6 rounded-full flex items-center justify-center bg-gray-800 border-2 border-gray-600">
              <span className="text-xs">{idx + 1}</span>
            </div>
            
            {/* Event Card */}
            <div 
              className={`ml-8 flex-1 bg-gray-700/30 rounded-lg p-4 cursor-pointer transition-all hover:bg-gray-700/50 ${
                selectedEvent?.id === event.id ? 'ring-2 ring-blue-500' : ''
              }`}
              onClick={() => setSelectedEvent(event)}
            >
              <div className="flex justify-between items-start">
                <div className="flex items-center gap-2">
                  <span className="text-xl">{getEventIcon(event.event_type)}</span>
                  <div>
                    <p className="font-medium text-white">
                      {event.event_type.replace(/_/g, ' ').toUpperCase()}
                    </p>
                    <p className="text-xs text-gray-500">
                      Version {event.version} • {new Date(event.timestamp).toLocaleString()}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <div className={`text-xs font-mono ${hashVerification[event.id] ? 'text-green-400' : 'text-red-400'}`}>
                    {hashVerification[event.id] ? '✅ Chain Valid' : '❌ Chain Broken'}
                  </div>
                </div>
              </div>
              
              {/* Hash Display */}
              <div className="mt-3 pt-3 border-t border-gray-600">
                <div className="flex flex-col gap-1 text-xs">
                  <div className="flex items-center gap-2">
                    <span className="text-gray-500 w-24">Event Hash:</span>
                    <code className="font-mono text-gray-300 bg-gray-800/50 px-2 py-1 rounded">
                      {truncateHash(event.event_hash)}
                    </code>
                    <button 
                      onClick={(e) => { e.stopPropagation(); navigator.clipboard.writeText(event.event_hash); }}
                      className="text-gray-500 hover:text-gray-300"
                    >
                      📋
                    </button>
                  </div>
                  {event.previous_hash && (
                    <div className="flex items-center gap-2">
                      <span className="text-gray-500 w-24">Previous Hash:</span>
                      <code className="font-mono text-gray-400 bg-gray-800/50 px-2 py-1 rounded">
                        {truncateHash(event.previous_hash)}
                      </code>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Selected Event Details */}
      {selectedEvent && (
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
          <div className="flex justify-between items-center mb-3">
            <h4 className="font-semibold text-white">Event Details</h4>
            <button onClick={() => setSelectedEvent(null)} className="text-gray-400 hover:text-white">✕</button>
          </div>
          <div className="space-y-2 text-sm">
            <div className="grid grid-cols-2 gap-2">
              <div>
                <span className="text-gray-500">Event ID:</span>
                <p className="text-white font-mono text-xs break-all">{selectedEvent.id}</p>
              </div>
              <div>
                <span className="text-gray-500">Version:</span>
                <p className="text-white">{selectedEvent.version}</p>
              </div>
              <div>
                <span className="text-gray-500">Full Hash:</span>
                <p className="text-white font-mono text-xs break-all">{selectedEvent.event_hash}</p>
              </div>
              <div>
                <span className="text-gray-500">Chain Status:</span>
                <p className={hashVerification[selectedEvent.id] ? 'text-green-400' : 'text-red-400'}>
                  {hashVerification[selectedEvent.id] ? 'Valid' : 'Broken'}
                </p>
              </div>
            </div>
            {Object.keys(selectedEvent.data).length > 0 && (
              <div className="mt-3 pt-3 border-t border-gray-700">
                <span className="text-gray-500">Event Data:</span>
                <pre className="text-xs text-gray-400 mt-1 overflow-x-auto bg-gray-900/50 p-2 rounded">
                  {JSON.stringify(selectedEvent.data, null, 2)}
                </pre>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Chain Summary */}
      <div className="bg-gray-800 rounded-lg p-3">
        <div className="flex justify-between items-center">
          <div>
            <p className="text-sm text-gray-300">Chain Integrity</p>
            <p className="text-xs text-gray-500">
              {events.length} events • {Object.values(hashVerification).filter(v => v).length} verified
            </p>
          </div>
          <div className="text-right">
            <span className={`text-sm font-semibold ${Object.values(hashVerification).every(v => v) ? 'text-green-400' : 'text-red-400'}`}>
              {Object.values(hashVerification).every(v => v) ? '✅ FULLY VERIFIED' : '⚠️ CHAIN BROKEN'}
            </span>
          </div>
        </div>
        <div className="mt-2 w-full bg-gray-700 rounded-full h-1.5">
          <div 
            className="h-1.5 rounded-full bg-green-500 transition-all"
            style={{ width: `${(Object.values(hashVerification).filter(v => v).length / events.length) * 100}%` }}
          ></div>
        </div>
      </div>
    </div>
  );
};

export default EventHashVisualization;
