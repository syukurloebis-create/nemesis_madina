import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { useAuthStore } from '../stores/authStore';
import { EventTimelineSlider } from '../components/temporal/EventTimelineSlider';

export default function TemporalReplay() {
  const { token } = useAuthStore();
  const [cases, setCases] = useState<any[]>([]);
  const [selectedCaseId, setSelectedCaseId] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [currentState, setCurrentState] = useState<any>(null);

  useEffect(() => {
    const fetchCases = async () => {
      if (!token) return;
      try {
        const response = await api.getCases();
        const casesData = response.data || response || [];
        setCases(casesData);
        if (casesData.length > 0) {
          setSelectedCaseId(casesData[0].id);
        }
      } catch (err) {
        console.error('Failed to fetch cases:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchCases();
  }, [token]);

  const handleVersionChange = async (version: number, state: any) => {
    setCurrentState(state);
    console.log(`State at version ${version}:`, state);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-500 mx-auto"></div>
          <p className="mt-4 text-gray-400">Memuat data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Pemutaran Temporal</h1>
        <p className="text-gray-400 mt-1">
          Navigasi melalui sejarah state kasus dengan event sourcing
        </p>
      </div>

      {/* Pilih Kasus */}
      <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
        <label className="block text-sm font-medium text-gray-300 mb-2">
          Pilih Kasus
        </label>
        <select
          value={selectedCaseId}
          onChange={(e) => setSelectedCaseId(e.target.value)}
          className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-cyan-500"
        >
          {cases.map((caseItem) => (
            <option key={caseItem.id} value={caseItem.id}>
              {caseItem.title} ({caseItem.status})
            </option>
          ))}
        </select>
      </div>

      {/* Timeline Slider */}
      {selectedCaseId && (
        <EventTimelineSlider 
          caseId={selectedCaseId} 
          onVersionChange={handleVersionChange}
        />
      )}

      {/* Current State Display */}
      {currentState && (
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <h3 className="text-sm font-medium text-gray-300 mb-3">State Saat Ini</h3>
          <pre className="text-xs text-gray-400 overflow-x-auto">
            {JSON.stringify(currentState, null, 2)}
          </pre>
        </div>
      )}

      {/* Info Panel */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 text-center">
          <div className="text-2xl font-bold text-cyan-400">Event Sourcing</div>
          <div className="text-xs text-gray-500 mt-1">Riwayat event lengkap tersimpan</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 text-center">
          <div className="text-2xl font-bold text-green-400">Hash Chain</div>
          <div className="text-xs text-gray-500 mt-1">Integritas kriptografis terverifikasi</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 text-center">
          <div className="text-2xl font-bold text-purple-400">Snapshots</div>
          <div className="text-xs text-gray-500 mt-1">State snapshot setiap versi</div>
        </div>
      </div>
    </div>
  );
}
