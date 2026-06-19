import React, { useEffect, useState } from 'react';
import CollusionGraph from '../../components/CollusionGraph';
import { getProcurementStats, getProcurementVendors } from '../../services/api';

interface Vendor {
  name: string;
  package_count: number;
  total_value: number;
  risk_score: string;
}

export default function ProcurementIntelligence() {
  const [stats, setStats] = useState<any>(null);
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [statsRes, vendorsRes] = await Promise.all([
        getProcurementStats(),
        getProcurementVendors(50)
      ]);
      setStats(statsRes.data);
      setVendors(vendorsRes.data?.vendors || []);
    } catch (err: any) {
      console.error('Failed to load procurement data:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const formatRupiah = (value: number) => {
    if (!value) return 'Rp0';
    // Format dengan pemisah ribuan
    return `Rp${value.toLocaleString('id-ID')}`;
  };

  const formatRupiahShort = (value: number) => {
    if (!value) return 'Rp0';
    if (value >= 1e9) return `Rp${(value / 1e9).toFixed(1)}M`;
    if (value >= 1e6) return `Rp${(value / 1e6).toFixed(0)}JT`;
    return `Rp${value.toLocaleString('id-ID')}`;
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="text-center py-12 text-gray-400">Memuat data intelijen pengadaan...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-900/20 border border-red-500 rounded-lg p-6">
          <p className="text-red-400 text-lg">⚠️ Gagal Memuat Data</p>
          <p className="text-gray-400 mt-2">{error}</p>
          <button onClick={loadData} className="mt-4 px-4 py-2 bg-cyan-600 rounded hover:bg-cyan-500">
            Coba Lagi
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-cyan-400 mb-2">Intelijen Pengadaan</h1>
      <p className="text-gray-400 mb-6">Data pengadaan lengkap, entitas vendor, dan pemetaan hubungan</p>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-gray-800 rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-cyan-400">{stats?.unique_vendors || 0}</div>
          <div className="text-gray-400 text-sm">Total Vendor</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-green-400">{stats?.total_packages || 0}</div>
          <div className="text-gray-400 text-sm">Total Paket</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-yellow-400">{formatRupiah(stats?.total_value || 0)}</div>
          <div className="text-gray-400 text-sm">Total Nilai</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-red-400">{stats?.collusion_edges || 0}</div>
          <div className="text-gray-400 text-sm">Tepi Kolusi</div>
        </div>
      </div>

      {/* Top Vendors by Contract */}
      <div className="bg-gray-800 rounded-lg p-4 mb-6">
        <h2 className="text-lg font-semibold text-cyan-400 mb-3">Vendor Teratas Berdasarkan Kontrak</h2>
        {vendors.length === 0 ? (
          <div className="text-center py-8 text-gray-500">Tidak ada data vendor</div>
        ) : (
          <div className="space-y-2">
            {vendors.slice(0, 10).map((vendor, idx) => (
              <div key={idx} className="flex justify-between items-center p-3 bg-gray-700/50 rounded">
                <div className="flex items-center gap-3">
                  <span className="text-cyan-400 font-bold w-6">{idx + 1}.</span>
                  <span className="text-gray-200">{vendor.name}</span>
                </div>
                <div className="flex gap-6">
                  <span className="text-gray-400">{vendor.package_count} kontrak</span>
                  <span className="text-green-400">{formatRupiahShort(vendor.total_value)}</span>
                  <span className={`px-2 py-0.5 rounded text-xs ${
                    vendor.risk_score === 'HIGH' ? 'bg-red-900/50 text-red-400' :
                    vendor.risk_score === 'MEDIUM' ? 'bg-yellow-900/50 text-yellow-400' : 'bg-green-900/50 text-green-400'
                  }`}>
                    {vendor.risk_score === 'HIGH' ? 'TINGGI' : vendor.risk_score === 'MEDIUM' ? 'SEDANG' : 'RENDAH'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Collusion Graph Section */}
      <CollusionGraph />

      {/* Footer */}
      <div className="mt-6 text-right text-gray-500 text-sm">
        Terakhir Diperbarui: {new Date().toLocaleString('id-ID')}
      </div>
    </div>
  );
}
