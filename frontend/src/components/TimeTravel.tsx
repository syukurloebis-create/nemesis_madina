import React, { useState } from 'react';
import { getTemporalState } from '../services/api';

interface TimeTravelProps {
  caseId: string;
  onStateLoaded?: (state: any) => void;
}

interface ReconstructedState {
  title?: string;
  description?: string;
  status?: string;
  priority?: string;
  assigned_to?: string | null;
  evidence?: any[];
  [key: string]: any;
}

export default function TimeTravel({ caseId, onStateLoaded }: TimeTravelProps) {
  const [timestamp, setTimestamp] = useState<string>(() => {
    // Default to current date and time
    const now = new Date();
    return now.toISOString().slice(0, 16);
  });
  const [loading, setLoading] = useState(false);
  const [state, setState] = useState<ReconstructedState | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showDiff, setShowDiff] = useState(false);
  const [currentState, setCurrentState] = useState<ReconstructedState | null>(null);

  const handleReconstruct = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await getTemporalState(caseId, timestamp);
      console.log('Reconstructed State:', response.data);
      setState(response.data.state || response.data);
      if (onStateLoaded) onStateLoaded(response.data.state || response.data);
    } catch (err: any) {
      console.error('Failed to reconstruct state:', err);
      setError(err.response?.data?.detail || err.message || 'Gagal merekonstruksi state');
    } finally {
      setLoading(false);
    }
  };

  const loadCurrentState = async () => {
    try {
      const now = new Date().toISOString();
      const response = await getTemporalState(caseId, now);
      setCurrentState(response.data.state || response.data);
    } catch (err) {
      console.error('Failed to load current state:', err);
    }
  };

  const handleCompare = async () => {
    if (!currentState) await loadCurrentState();
    setShowDiff(true);
  };

  const getDiff = () => {
    if (!state || !currentState) return [];
    const changes = [];
    const allKeys = new Set([...Object.keys(state), ...Object.keys(currentState)]);
    
    for (const key of allKeys) {
      const oldVal = state[key];
      const newVal = currentState[key];
      if (JSON.stringify(oldVal) !== JSON.stringify(newVal)) {
        changes.push({
          field: key,
          old_value: oldVal,
          new_value: newVal
        });
      }
    }
    return changes;
  };

  const formatTimestamp = (isoString: string) => {
    const date = new Date(isoString);
    return date.toLocaleString('id-ID', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="bg-gray-800 rounded-lg p-4 mb-6">
      <h3 className="text-lg font-semibold text-cyan-400 mb-3 flex items-center gap-2">
        <span>⏰</span> Historical Reconstruction (Time Travel)
      </h3>
      
      <div className="flex flex-wrap gap-4 items-end mb-4">
        <div className="flex-1 min-w-[200px]">
          <label className="block text-gray-400 text-sm mb-1">Select Timestamp</label>
          <input
            type="datetime-local"
            value={timestamp}
            onChange={(e) => setTimestamp(e.target.value)}
            className="w-full px-3 py-2 bg-gray-700 rounded text-white"
          />
        </div>
        <button
          onClick={handleReconstruct}
          disabled={loading}
          className="px-4 py-2 bg-cyan-600 rounded hover:bg-cyan-500 disabled:opacity-50"
        >
          {loading ? 'Reconstructing...' : '🔍 Reconstruct State'}
        </button>
        {state && (
          <button
            onClick={handleCompare}
            className="px-4 py-2 bg-purple-600 rounded hover:bg-purple-500"
          >
            📊 Compare with Current
          </button>
        )}
      </div>

      {error && (
        <div className="bg-red-900/20 border border-red-500 rounded-lg p-3 mb-4">
          <p className="text-red-400 text-sm">{error}</p>
        </div>
      )}

      {state && (
        <div className="mt-4">
          <h4 className="text-md font-semibold text-gray-300 mb-2">
            Reconstructed State at {formatTimestamp(timestamp)}
          </h4>
          <div className="bg-gray-900 rounded-lg p-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-gray-400 text-sm">Title</p>
                <p className="text-white font-medium">{state.title || '-'}</p>
              </div>
              <div>
                <p className="text-gray-400 text-sm">Status</p>
                <p className={`font-medium ${state.status === 'OPEN' ? 'text-green-400' : 'text-yellow-400'}`}>
                  {state.status || '-'}
                </p>
              </div>
              <div>
                <p className="text-gray-400 text-sm">Priority</p>
                <p className={`font-medium ${
                  state.priority === 'HIGH' ? 'text-red-400' :
                  state.priority === 'MEDIUM' ? 'text-yellow-400' : 'text-blue-400'
                }`}>
                  {state.priority || '-'}
                </p>
              </div>
              <div>
                <p className="text-gray-400 text-sm">Assigned To</p>
                <p className="text-white">{state.assigned_to || 'Unassigned'}</p>
              </div>
            </div>
            {state.description && (
              <div className="mt-3">
                <p className="text-gray-400 text-sm">Description</p>
                <p className="text-gray-300 text-sm">{state.description}</p>
              </div>
            )}
            {state.evidence && state.evidence.length > 0 && (
              <div className="mt-3">
                <p className="text-gray-400 text-sm">Evidence ({state.evidence.length})</p>
                <div className="flex flex-wrap gap-2 mt-1">
                  {state.evidence.slice(0, 3).map((e: any, idx: number) => (
                    <span key={idx} className="text-xs bg-gray-700 px-2 py-1 rounded text-gray-300">
                      📄 {e.title || e.evidence_id?.slice(0, 8)}
                    </span>
                  ))}
                  {state.evidence.length > 3 && (
                    <span className="text-xs text-gray-500">+{state.evidence.length - 3} more</span>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {showDiff && currentState && (
        <div className="mt-4">
          <h4 className="text-md font-semibold text-gray-300 mb-2">Changes from Selected Time to Current</h4>
          <div className="bg-gray-900 rounded-lg p-4">
            {getDiff().length === 0 ? (
              <p className="text-gray-400 text-center">No changes detected</p>
            ) : (
              <div className="space-y-2">
                {getDiff().map((change, idx) => (
                  <div key={idx} className="border-b border-gray-700 pb-2">
                    <p className="text-sm font-medium text-cyan-400">{change.field}</p>
                    <div className="grid grid-cols-2 gap-2 mt-1 text-sm">
                      <div>
                        <span className="text-gray-500">Before:</span>
                        <p className="text-gray-400">{JSON.stringify(change.old_value) || '-'}</p>
                      </div>
                      <div>
                        <span className="text-gray-500">Now:</span>
                        <p className="text-gray-200">{JSON.stringify(change.new_value) || '-'}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
