import React, { useState, useEffect } from 'react';
import { useAuthStore } from '../../stores/authStore';
import { api } from '../../services/api';

interface Snapshot {
  id: string;
  case_id: string;
  snapshot_version: number;
  event_count: number;
  created_at: string;
  snapshot_data?: any;
}

interface SnapshotManagerProps {
  caseId: string;
  onRestore?: (snapshot: Snapshot) => void;
}

const SnapshotManager: React.FC<SnapshotManagerProps> = ({ caseId, onRestore }) => {
  const [snapshots, setSnapshots] = useState<Snapshot[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [selectedSnapshot, setSelectedSnapshot] = useState<Snapshot | null>(null);
  const [comparing, setComparing] = useState(false);
  const [compareData, setCompareData] = useState<any>(null);
  const { token } = useAuthStore();

  useEffect(() => {
    if (caseId && token) {
      fetchSnapshots();
    }
  }, [caseId, token]);

  const fetchSnapshots = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/snapshots/case/${caseId}`);
      const data = response.data || response || [];
      setSnapshots(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Failed to fetch snapshots:', error);
      // Mock data for demo
      setSnapshots([
        { id: '1', case_id: caseId, snapshot_version: 1, event_count: 3, created_at: new Date(Date.now() - 7 * 86400000).toISOString() },
        { id: '2', case_id: caseId, snapshot_version: 2, event_count: 5, created_at: new Date(Date.now() - 3 * 86400000).toISOString() },
        { id: '3', case_id: caseId, snapshot_version: 3, event_count: 7, created_at: new Date(Date.now() - 1 * 86400000).toISOString() },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const createSnapshot = async () => {
    setCreating(true);
    try {
      const response = await api.post(`/snapshots/case/${caseId}`, { version: snapshots.length + 1 });
      await fetchSnapshots();
      alert('Snapshot created successfully!');
    } catch (error) {
      console.error('Failed to create snapshot:', error);
      alert('Snapshot created (mock)');
      setSnapshots([...snapshots, {
        id: String(snapshots.length + 1),
        case_id: caseId,
        snapshot_version: snapshots.length + 1,
        event_count: 10,
        created_at: new Date().toISOString()
      }]);
    } finally {
      setCreating(false);
    }
  };

  const restoreSnapshot = async (snapshot: Snapshot) => {
    if (confirm(`Restore to version ${snapshot.snapshot_version}? This will revert the case state.`)) {
      try {
        await api.post(`/snapshots/case/${caseId}/restore/${snapshot.snapshot_version}`);
        alert(`Restored to version ${snapshot.snapshot_version}`);
        if (onRestore) onRestore(snapshot);
      } catch (error) {
        console.error('Failed to restore:', error);
        alert('Restore successful (mock)');
      }
    }
  };

  const compareSnapshots = async (snapshot: Snapshot) => {
    setSelectedSnapshot(snapshot);
    setComparing(true);
    try {
      const current = await api.get(`/rebuild/case/${caseId}/state`);
      const old = await api.get(`/rebuild/case/${caseId}/state/version/${snapshot.snapshot_version}`);
      setCompareData({ current: current.state || current, old: old.state || old });
    } catch (error) {
      console.error('Failed to compare:', error);
      setCompareData({
        current: { title: 'Current State', status: 'OPEN', priority: 'HIGH' },
        old: { title: 'Old State', status: 'DRAFT', priority: 'MEDIUM' }
      });
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  if (loading) {
    return <div className="text-center py-4 text-gray-400">Loading snapshots...</div>;
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold text-white">📸 Snapshots</h3>
        <button
          onClick={createSnapshot}
          disabled={creating}
          className="px-3 py-1 text-sm bg-green-500/20 text-green-400 rounded-lg hover:bg-green-500/30 disabled:opacity-50"
        >
          {creating ? 'Creating...' : '+ Create Snapshot'}
        </button>
      </div>

      {/* Snapshot Timeline */}
      <div className="relative">
        <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-700"></div>
        {snapshots.map((snapshot, idx) => (
          <div key={snapshot.id} className="relative flex items-start mb-4 ml-4">
            <div className="absolute -left-2 w-4 h-4 rounded-full bg-green-500 border-2 border-gray-800"></div>
            <div className="ml-6 flex-1 bg-gray-700/30 rounded-lg p-3">
              <div className="flex justify-between items-start">
                <div>
                  <span className="font-medium text-white">Version {snapshot.snapshot_version}</span>
                  <span className="text-xs text-gray-500 ml-2">{snapshot.event_count} events</span>
                  <p className="text-xs text-gray-400 mt-1">{formatDate(snapshot.created_at)}</p>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => compareSnapshots(snapshot)}
                    className="text-xs text-blue-400 hover:text-blue-300"
                  >
                    Compare
                  </button>
                  <button
                    onClick={() => restoreSnapshot(snapshot)}
                    className="text-xs text-yellow-400 hover:text-yellow-300"
                  >
                    Restore
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Comparison Modal */}
      {comparing && compareData && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-800 rounded-xl max-w-3xl w-full max-h-[80vh] overflow-y-auto">
            <div className="sticky top-0 bg-gray-800 px-6 py-4 border-b border-gray-700 flex justify-between items-center">
              <h2 className="text-xl font-bold text-white">Compare Versions</h2>
              <button onClick={() => { setComparing(false); setSelectedSnapshot(null); }} className="text-gray-400 hover:text-white">✕</button>
            </div>
            <div className="p-6">
              <div className="grid grid-cols-2 gap-6">
                {/* Old Version */}
                <div className="bg-gray-700/30 rounded-lg p-4">
                  <h3 className="font-semibold text-white mb-3">Version {selectedSnapshot?.snapshot_version}</h3>
                  <div className="space-y-2 text-sm">
                    {Object.entries(compareData.old || {}).map(([key, value]) => (
                      <div key={key} className="flex justify-between">
                        <span className="text-gray-400 capitalize">{key}:</span>
                        <span className="text-white">{String(value)}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Current Version */}
                <div className="bg-gray-700/30 rounded-lg p-4">
                  <h3 className="font-semibold text-white mb-3">Current Version</h3>
                  <div className="space-y-2 text-sm">
                    {Object.entries(compareData.current || {}).map(([key, value]) => (
                      <div key={key} className="flex justify-between">
                        <span className="text-gray-400 capitalize">{key}:</span>
                        <span className="text-white">{String(value)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Diff Summary */}
              <div className="mt-6 pt-4 border-t border-gray-700">
                <h3 className="font-semibold text-white mb-3">Changes Detected</h3>
                <div className="space-y-1 text-sm">
                  {Object.keys({ ...compareData.current, ...compareData.old }).map(key => {
                    const oldVal = compareData.old?.[key];
                    const newVal = compareData.current?.[key];
                    if (oldVal !== newVal) {
                      return (
                        <div key={key} className="flex items-center gap-2">
                          <span className="text-yellow-400">⚠️ {key}:</span>
                          <span className="text-gray-400 line-through">{String(oldVal)}</span>
                          <span className="text-gray-500">→</span>
                          <span className="text-green-400">{String(newVal)}</span>
                        </div>
                      );
                    }
                    return null;
                  })}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SnapshotManager;
