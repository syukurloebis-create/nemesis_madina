import React, { useEffect, useState } from 'react';
import { getChainIntegrity } from '../services/api';

interface ChainIntegrityData {
  total_agregat: number;
  total_event: number;
  status: string;
  status_text: string;
  detail?: Array<{
    tipe: string;
    id: string;
    jumlah_event: number;
  }>;
}

export default function ChainIntegrity() {
  const [data, setData] = useState<ChainIntegrityData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await getChainIntegrity();
      console.log('Chain Integrity Data:', response.data);
      setData(response.data);
    } catch (err: any) {
      console.error('Failed to load chain integrity:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-gray-800 rounded-lg p-4 animate-pulse">
        <div className="h-4 bg-gray-700 rounded w-1/2 mb-3"></div>
        <div className="h-8 bg-gray-700 rounded w-full mb-2"></div>
        <div className="h-4 bg-gray-700 rounded w-3/4"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-gray-800 rounded-lg p-4">
        <div className="flex items-center gap-2 text-red-400">
          <span className="text-lg">⚠️</span>
          <span className="text-sm">Gagal memuat data integritas</span>
        </div>
        <button onClick={loadData} className="mt-2 text-xs text-cyan-400 hover:text-cyan-300">
          Coba lagi
        </button>
      </div>
    );
  }

  const isHealthy = data?.status === 'HEALTHY';
  const statusColor = isHealthy ? 'text-green-400' : 'text-red-400';
  const statusBg = isHealthy ? 'bg-green-900/20' : 'bg-red-900/20';
  const statusBorder = isHealthy ? 'border-green-500' : 'border-red-500';

  return (
    <div className={`bg-gray-800 rounded-lg p-4 border-l-4 ${statusBorder}`}>
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-gray-300">🔗 Integritas Rantai</h3>
        <div className={`flex items-center gap-1 px-2 py-0.5 rounded-full text-xs ${statusBg} ${statusColor}`}>
          <span>{isHealthy ? '✅' : '⚠️'}</span>
          <span>{data?.status_text || data?.status || 'Unknown'}</span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3 mb-3">
        <div className="text-center">
          <div className="text-2xl font-bold text-cyan-400">{data?.total_agregat || 0}</div>
          <div className="text-xs text-gray-500">Total Agregat</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-blue-400">{data?.total_event || 0}</div>
          <div className="text-xs text-gray-500">Total Event</div>
        </div>
      </div>

      {data?.detail && data.detail.length > 0 && (
        <div className="mt-3 pt-3 border-t border-gray-700">
          <p className="text-xs text-gray-500 mb-2">Detail Agregat:</p>
          <div className="space-y-1 max-h-32 overflow-y-auto">
            {data.detail.slice(0, 5).map((item, idx) => (
              <div key={idx} className="flex justify-between text-xs">
                <span className="text-gray-400 truncate max-w-[150px]">{item.tipe}</span>
                <span className="text-gray-500">{item.jumlah_event} event</span>
              </div>
            ))}
            {data.detail.length > 5 && (
              <p className="text-xs text-gray-600">+{data.detail.length - 5} lainnya</p>
            )}
          </div>
        </div>
      )}

      <div className="mt-3 text-right">
        <button
          onClick={loadData}
          className="text-xs text-gray-500 hover:text-gray-400 transition"
        >
          🔄 Refresh
        </button>
      </div>
    </div>
  );
}
