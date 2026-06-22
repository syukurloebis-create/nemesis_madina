// src/pages/menu/CasesMenu.tsx - Cases Management (FIXED)
import React, { useState, useEffect } from 'react';
import api from '../../services/api';

interface Case {
  id: string;
  title: string;
  status: string;
  risk_score: number;
  risk_level: string;
  created_at: string;
  evidence_count: number;
}

export const CasesMenu: React.FC<{ caseId?: string }> = ({ caseId }) => {
  const [cases, setCases] = useState<Case[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [casesRes, statsRes] = await Promise.all([
          api.get('/api/v1/cases/'),
          api.get('/api/v1/cases/stats')
        ]);
        setCases(casesRes.data || []);
        setStats(statsRes.data || {});
        setError(null);
      } catch (err) {
        setError('Gagal memuat data kasus');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-500/10 border border-red-500/30 p-6 rounded-xl text-red-400">
        <p>{error}</p>
        <button onClick={() => window.location.reload()} className="mt-4 px-4 py-2 bg-red-600 rounded-lg">
          Coba Lagi
        </button>
      </div>
    );
  }

  // ============ FIX: Menampilkan 6 kasus ============
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white">📋 Manajemen Kasus</h2>
        <div className="flex gap-4 text-sm">
          <span className="text-gray-400">Total: <span className="text-white font-bold">{stats?.total || 0}</span></span>
          <span className="text-blue-400">Terbuka: {stats?.open || 0}</span>
          <span className="text-yellow-400">Investigasi: {stats?.investigating || 0}</span>
          <span className="text-green-400">Selesai: {stats?.closed || 0}</span>
        </div>
      </div>

      {cases.length === 0 ? (
        <div className="bg-dark-card rounded-xl shadow-lg border border-gray-700/50 p-8 text-center">
          <p className="text-gray-400">Belum ada kasus</p>
        </div>
      ) : (
        <div className="grid gap-4">
          {cases.map((c) => (
            <div key={c.id} className="bg-dark-card rounded-xl shadow-lg border border-gray-700/50 p-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-white font-medium">{c.title}</h3>
                  <p className="text-sm text-gray-400">Status: {c.status}</p>
                  <p className="text-xs text-gray-500">Dibuat: {new Date(c.created_at).toLocaleDateString('id-ID')}</p>
                </div>
                <div className="text-right">
                  <span className={`px-3 py-1 rounded-full text-sm ${
                    c.risk_level === 'HIGH' ? 'bg-red-500/30 text-red-400' :
                    c.risk_level === 'MEDIUM' ? 'bg-yellow-500/30 text-yellow-400' :
                    'bg-green-500/30 text-green-400'
                  }`}>
                    {c.risk_level}
                  </span>
                  <p className="text-xs text-gray-500 mt-1">Evidence: {c.evidence_count || 0}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default CasesMenu;
