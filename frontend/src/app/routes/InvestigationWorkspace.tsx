import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { getCase, getCaseTimeline, getEvidence } from '../../services/api';

interface Case {
  id: string;
  title: string;
  description: string;
  status: string;
  priority: string;
  created_at: string;
}

interface TimelineEvent {
  id: string;
  event_type: string;
  version: number;
  timestamp: string;
  payload: any;
  event_hash: string;
}

interface EvidenceItem {
  id: string;
  filename: string;
  sha256_hash: string;
  uploaded_at: string;
  integrity_status: string;
  file_size: number;
}

export default function InvestigationWorkspace() {
  const { caseId } = useParams<{ caseId: string }>();
  const [currentCase, setCurrentCase] = useState<Case | null>(null);
  const [timeline, setTimeline] = useState<TimelineEvent[]>([]);
  const [evidence, setEvidence] = useState<EvidenceItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTimestamp, setSelectedTimestamp] = useState('');
  const [reconstructedState, setReconstructedState] = useState<any>(null);
  const [reconstructing, setReconstructing] = useState(false);

  useEffect(() => {
    if (caseId) {
      loadAllData();
    }
  }, [caseId]);

  const loadAllData = async () => {
    if (!caseId) return;

    setLoading(true);
    setError(null);
    try {
      const [caseRes, timelineRes, evidenceRes] = await Promise.all([
        getCase(caseId).catch(() => ({ data: null })),
        getCaseTimeline(caseId, 50).catch(() => ({ data: { timeline: [] } })),
        getEvidence(caseId).catch(() => ({ data: { evidence: [] } }))
      ]);
      
      setCurrentCase(caseRes.data);
      setTimeline(timelineRes.data?.timeline || []);
      setEvidence(evidenceRes.data?.evidence || []);
    } catch (err: any) {
      console.error('Failed to load data:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleTimeTravel = async () => {
    if (!caseId || !selectedTimestamp) return;
    setReconstructing(true);
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/historical/case/${caseId}/state-at-time?timestamp=${selectedTimestamp}`);
      const data = await response.json();
      setReconstructedState(data.state || data);
    } catch (err) {
      console.error('Time travel failed:', err);
    } finally {
      setReconstructing(false);
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="text-center py-12 text-gray-400">Loading investigation data...</div>
      </div>
    );
  }

  if (error || !currentCase) {
    return (
      <div className="p-6">
        <div className="bg-red-900/20 border border-red-500 rounded-lg p-6">
          <p className="text-red-400 text-lg">⚠️ Error Loading Case</p>
          <p className="text-gray-400 mt-2">{error || 'Case not found'}</p>
          <button onClick={loadAllData} className="mt-4 px-4 py-2 bg-cyan-600 rounded hover:bg-cyan-500">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-cyan-400 mb-4">Investigation Workspace</h1>

      {/* Case Header */}
      <div className="bg-gray-800 rounded-lg p-6 mb-6">
        <h2 className="text-xl font-semibold text-white mb-2">{currentCase.title}</h2>
        <p className="text-gray-400 mb-4">{currentCase.description || 'No description'}</p>
        <div className="flex flex-wrap gap-4">
          <div className="bg-gray-700 rounded px-3 py-1">
            <span className="text-gray-400">Status:</span>
            <span className={`ml-2 ${currentCase.status === 'OPEN' ? 'text-green-400' : 'text-yellow-400'}`}>
              {currentCase.status}
            </span>
          </div>
          <div className="bg-gray-700 rounded px-3 py-1">
            <span className="text-gray-400">Priority:</span>
            <span className={`ml-2 ${
              currentCase.priority === 'HIGH' ? 'text-red-400' :
              currentCase.priority === 'MEDIUM' ? 'text-yellow-400' : 'text-blue-400'
            }`}>
              {currentCase.priority}
            </span>
          </div>
          <div className="bg-gray-700 rounded px-3 py-1">
            <span className="text-gray-400">Created:</span>
            <span className="ml-2 text-gray-300">
              {new Date(currentCase.created_at).toLocaleString()}
            </span>
          </div>
        </div>
      </div>

      {/* Timeline Panel */}
      <div className="bg-gray-800 rounded-lg p-4 mb-6">
        <h3 className="text-lg font-semibold text-cyan-400 mb-3">📅 Timeline</h3>
        {timeline.length === 0 ? (
          <div className="text-gray-400 text-center py-8">No events recorded yet</div>
        ) : (
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {timeline.map((event, idx) => (
              <div key={idx} className="border-b border-gray-700 pb-2">
                <div className="flex justify-between items-center">
                  <span className="text-cyan-400 text-sm font-mono">v{event.version}</span>
                  <span className="text-gray-500 text-xs">{new Date(event.timestamp).toLocaleString()}</span>
                </div>
                <p className="text-gray-300 text-sm mt-1">{event.event_type}</p>
                {event.payload && (
                  <div className="text-gray-500 text-xs mt-1">
                    {event.payload.title && <span>Title: {event.payload.title.substring(0, 50)}</span>}
                  </div>
                )}
                <p className="text-gray-600 text-xs font-mono mt-1">Hash: {event.event_hash?.substring(0, 16)}...</p>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Evidence Panel */}
        <div className="bg-gray-800 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-cyan-400 mb-3">📎 Evidence</h3>
          {evidence.length === 0 ? (
            <div className="text-gray-400 text-center py-8">No evidence uploaded yet</div>
          ) : (
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {evidence.map((item) => (
                <div key={item.id} className="border-b border-gray-700 pb-2">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-300 text-sm">{item.filename}</span>
                    <span className={`text-xs px-2 py-0.5 rounded ${
                      item.integrity_status === 'verified' ? 'bg-green-900/50 text-green-400' : 'bg-yellow-900/50 text-yellow-400'
                    }`}>
                      {item.integrity_status || 'pending'}
                    </span>
                  </div>
                  <p className="text-gray-500 text-xs mt-1">Size: {Math.round(item.file_size / 1024)} KB</p>
                  <p className="text-gray-600 text-xs font-mono">SHA256: {item.sha256_hash?.substring(0, 16)}...</p>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Time Travel Panel */}
        <div className="bg-gray-800 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-cyan-400 mb-3">⏰ Time Travel</h3>
          <div className="flex flex-wrap gap-4 items-end">
            <div className="flex-1">
              <label className="block text-gray-400 text-sm mb-1">Select Timestamp</label>
              <input
                type="datetime-local"
                value={selectedTimestamp}
                onChange={(e) => setSelectedTimestamp(e.target.value)}
                className="w-full px-3 py-2 bg-gray-700 rounded text-white"
              />
            </div>
            <button
              onClick={handleTimeTravel}
              disabled={!selectedTimestamp || reconstructing}
              className="px-4 py-2 bg-cyan-600 rounded hover:bg-cyan-500 disabled:opacity-50"
            >
              {reconstructing ? 'Reconstructing...' : '🔍 Reconstruct State'}
            </button>
          </div>
          {reconstructedState && (
            <div className="mt-4 bg-gray-900 rounded-lg p-3">
              <h4 className="text-sm font-semibold text-gray-300 mb-2">Reconstructed State</h4>
              <pre className="text-xs text-gray-400 overflow-x-auto">
                {JSON.stringify(reconstructedState, null, 2)}
              </pre>
            </div>
          )}
        </div>
      </div>

      {/* Event Stream Panel */}
      <div className="bg-gray-800 rounded-lg p-4 mb-6">
        <h3 className="text-lg font-semibold text-cyan-400 mb-3">📡 Event Stream</h3>
        <div className="space-y-1 max-h-48 overflow-y-auto">
          {timeline.slice(0, 10).map((event, idx) => (
            <div key={idx} className="text-sm border-l-2 border-cyan-500 pl-3 py-1">
              <span className="text-gray-500 text-xs">{new Date(event.timestamp).toLocaleTimeString()}</span>
              {' - '}
              <span className="text-gray-300">{event.event_type}</span>
            </div>
          ))}
          {timeline.length === 0 && (
            <div className="text-gray-400 text-center py-4">No events in stream</div>
          )}
        </div>
      </div>

      {/* Footer Stats */}
      <div className="text-right text-gray-500 text-sm">
        Total Events: {timeline.length} | Evidence: {evidence.length}
      </div>
    </div>
  );
}
