import React, { useState, useEffect } from 'react';
import { useAuthStore } from '../../stores/authStore';
import { api } from '../../services/api';

interface StateSnapshot {
  version: number;
  timestamp: string;
  state: Record<string, any>;
  event_type: string;
  event_hash: string;
}

interface VersionedStateExplorerProps {
  caseId: string;
}

const VersionedStateExplorer: React.FC<VersionedStateExplorerProps> = ({ caseId }) => {
  const [states, setStates] = useState<StateSnapshot[]>([]);
  const [selectedVersion, setSelectedVersion] = useState<number | null>(null);
  const [selectedState, setSelectedState] = useState<Record<string, any> | null>(null);
  const [loading, setLoading] = useState(true);
  const [timeline, setTimeline] = useState<any[]>([]);
  const { token } = useAuthStore();

  useEffect(() => {
    if (caseId && token) {
      fetchVersionedStates();
    }
  }, [caseId, token]);

  const fetchVersionedStates = async () => {
    try {
      setLoading(true);
      const timelineData = await api.getCaseTimeline(caseId);
      const events = timelineData.timeline || timelineData;
      
      const stateSnapshots: StateSnapshot[] = [];
      let currentState: Record<string, any> = {};
      
      for (let i = 0; i < events.length; i++) {
        const event = events[i];
        // Apply event to state
        if (event.event_type === 'case_created') {
          currentState = { ...event.data, version: event.version, status: 'OPEN' };
        } else if (event.event_type === 'case_assigned') {
          currentState = { ...currentState, assigned_to: event.data.assignee, status: 'INVESTIGATING' };
        } else if (event.event_type === 'evidence_added') {
          const evidenceList = currentState.evidence_list || [];
          evidenceList.push(event.data);
          currentState = { ...currentState, evidence_list: evidenceList };
        } else if (event.event_type === 'status_changed') {
          currentState = { ...currentState, status: event.data.new_status };
        } else if (event.event_type === 'case_closed') {
          currentState = { ...currentState, status: 'CLOSED', resolution: event.data.resolution };
        } else {
          currentState = { ...currentState, ...event.data };
        }
        
        stateSnapshots.push({
          version: event.version,
          timestamp: event.timestamp,
          state: { ...currentState, version: event.version },
          event_type: event.event_type,
          event_hash: event.event_hash
        });
      }
      
      setStates(stateSnapshots);
      setTimeline(events);
      if (stateSnapshots.length > 0) {
        setSelectedVersion(stateSnapshots[stateSnapshots.length - 1].version);
        setSelectedState(stateSnapshots[stateSnapshots.length - 1].state);
      }
    } catch (error) {
      console.error('Failed to fetch versioned states:', error);
      // Mock data
      const mockStates: StateSnapshot[] = [
        { version: 1, timestamp: new Date().toISOString(), state: { title: 'Fraud Investigation', status: 'OPEN', priority: 'HIGH' }, event_type: 'case_created', event_hash: 'hash1' },
        { version: 2, timestamp: new Date(Date.now() - 3600000).toISOString(), state: { title: 'Fraud Investigation', status: 'INVESTIGATING', priority: 'HIGH', assigned_to: 'investigator' }, event_type: 'case_assigned', event_hash: 'hash2' },
        { version: 3, timestamp: new Date(Date.now() - 7200000).toISOString(), state: { title: 'Fraud Investigation', status: 'INVESTIGATING', priority: 'HIGH', assigned_to: 'investigator', evidence: ['Financial Report'] }, event_type: 'evidence_added', event_hash: 'hash3' },
      ];
      setStates(mockStates);
      setSelectedVersion(3);
      setSelectedState(mockStates[2].state);
    } finally {
      setLoading(false);
    }
  };

  const navigateToVersion = (version: number) => {
    const state = states.find(s => s.version === version);
    if (state) {
      setSelectedVersion(version);
      setSelectedState(state.state);
    }
  };

  const getStateDiff = (version1: number, version2: number) => {
    const state1 = states.find(s => s.version === version1)?.state;
    const state2 = states.find(s => s.version === version2)?.state;
    if (!state1 || !state2) return [];
    
    const allKeys = new Set([...Object.keys(state1), ...Object.keys(state2)]);
    const diffs = [];
    for (const key of allKeys) {
      if (JSON.stringify(state1[key]) !== JSON.stringify(state2[key])) {
        diffs.push({
          key,
          from: state1[key],
          to: state2[key]
        });
      }
    }
    return diffs;
  };

  const [compareVersion, setCompareVersion] = useState<number | null>(null);
  const [diffs, setDiffs] = useState<any[]>([]);

  useEffect(() => {
    if (compareVersion && selectedVersion) {
      setDiffs(getStateDiff(compareVersion, selectedVersion));
    }
  }, [compareVersion, selectedVersion]);

  if (loading) {
    return <div className="text-center py-8 text-gray-400">Loading state explorer...</div>;
  }

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-semibold text-white">📜 Versioned State Explorer</h3>

      {/* Version Timeline Slider */}
      <div className="space-y-3">
        <div className="flex justify-between text-sm text-gray-400">
          <span>Version {selectedVersion || 1} of {states.length}</span>
          <span>State Evolution Timeline</span>
        </div>
        <input
          type="range"
          min={1}
          max={states.length}
          value={selectedVersion || 1}
          onChange={(e) => navigateToVersion(parseInt(e.target.value))}
          className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
        />
        <div className="flex justify-between text-xs text-gray-500">
          {states.map((state) => (
            <div key={state.version} className="text-center">
              <div className={`w-2 h-2 rounded-full mx-auto mb-1 ${selectedVersion === state.version ? 'bg-green-500' : 'bg-gray-600'}`}></div>
              <span>v{state.version}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Current State Display */}
      {selectedState && (
        <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-4">
          <div className="flex justify-between items-center mb-3">
            <h4 className="font-semibold text-white">State at Version {selectedVersion}</h4>
            <span className="text-xs text-gray-500">
              {states.find(s => s.version === selectedVersion)?.event_type}
            </span>
          </div>
          <div className="grid grid-cols-2 gap-3 text-sm">
            {Object.entries(selectedState).map(([key, value]) => (
              <div key={key} className="flex justify-between border-b border-gray-700 pb-1">
                <span className="text-gray-400 capitalize">{key}:</span>
                <span className="text-white">{String(value)}</span>
              </div>
            ))}
          </div>
          <div className="mt-3 pt-3 border-t border-gray-700">
            <div className="flex justify-between text-xs">
              <span className="text-gray-500">Event Hash:</span>
              <code className="text-gray-400 font-mono">
                {states.find(s => s.version === selectedVersion)?.event_hash?.substring(0, 24)}...
              </code>
            </div>
          </div>
        </div>
      )}

      {/* Version Comparison Tool */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 p-4">
        <h4 className="font-semibold text-white mb-3">Compare Versions</h4>
        <div className="grid grid-cols-2 gap-4 mb-4">
          <select
            value={compareVersion || ''}
            onChange={(e) => setCompareVersion(parseInt(e.target.value))}
            className="px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white text-sm"
          >
            <option value="">Select version to compare</option>
            {states.map(s => (
              <option key={s.version} value={s.version} disabled={s.version === selectedVersion}>
                Version {s.version}
              </option>
            ))}
          </select>
          <div className="text-center text-gray-500 text-sm">
            vs Current: v{selectedVersion}
          </div>
        </div>
        
        {diffs.length > 0 && (
          <div className="space-y-2">
            <p className="text-sm text-gray-400">Changes detected:</p>
            {diffs.map((diff, idx) => (
              <div key={idx} className="bg-yellow-500/10 border border-yellow-500/30 rounded p-2 text-sm">
                <div className="flex items-center gap-2">
                  <span className="text-yellow-400">⚠️</span>
                  <span className="text-gray-300 capitalize">{diff.key}:</span>
                  <span className="text-gray-500 line-through">{String(diff.from)}</span>
                  <span className="text-gray-600">→</span>
                  <span className="text-green-400">{String(diff.to)}</span>
                </div>
              </div>
            ))}
          </div>
        )}
        {compareVersion && diffs.length === 0 && (
          <div className="text-center text-gray-500 text-sm">No changes between versions</div>
        )}
      </div>

      {/* State Version List */}
      <div className="space-y-2 max-h-64 overflow-y-auto">
        <h4 className="font-semibold text-white">Version History</h4>
        {states.map((state) => (
          <div
            key={state.version}
            className={`p-3 rounded-lg cursor-pointer transition-colors ${
              selectedVersion === state.version
                ? 'bg-green-500/20 border border-green-500/30'
                : 'bg-gray-700/30 hover:bg-gray-700/50'
            }`}
            onClick={() => navigateToVersion(state.version)}
          >
            <div className="flex justify-between items-center">
              <div>
                <span className="font-medium text-white">Version {state.version}</span>
                <span className="text-xs text-gray-500 ml-2">{state.event_type}</span>
              </div>
              <span className="text-xs text-gray-500">
                {new Date(state.timestamp).toLocaleString()}
              </span>
            </div>
            <div className="mt-1 text-xs text-gray-400">
              Status: {state.state.status || 'UNKNOWN'}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default VersionedStateExplorer;
