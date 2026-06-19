import React, { useState, useEffect } from 'react';
import { useAuthStore } from '../stores/authStore';
import { procurementService } from '../services/procurementService';
import type { ProcurementPackage, ProcurementStats } from '../types/procurement';

const ProcurementDashboard: React.FC = () => {
  const [packages, setPackages] = useState<ProcurementPackage[]>([]);
  const [stats, setStats] = useState<ProcurementStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const { token } = useAuthStore();

  useEffect(() => {
    fetchData();
  }, [filterStatus]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [pkgData, statsData] = await Promise.all([
        procurementService.getPackages(filterStatus === 'all' ? {} : { status: filterStatus }),
        procurementService.getStats()
      ]);
      setPackages(pkgData);
      setStats(statsData);
    } catch (error) {
      console.error('Failed to fetch procurement data:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(value);
  };

  const getStatusBadge = (status: string) => {
    const colors: Record<string, string> = {
      planning: 'bg-blue-500/20 text-blue-400',
      tendering: 'bg-yellow-500/20 text-yellow-400',
      contract: 'bg-green-500/20 text-green-400',
      completed: 'bg-gray-500/20 text-gray-400',
      cancelled: 'bg-red-500/20 text-red-400'
    };
    const labels: Record<string, string> = {
      planning: 'Perencanaan',
      tendering: 'Tender',
      contract: 'Kontrak',
      completed: 'Selesai',
      cancelled: 'Batal'
    };
    return { color: colors[status] || 'bg-gray-500/20 text-gray-400', label: labels[status] || status };
  };

  const getRiskBadge = (score?: number) => {
    if (!score) return { color: 'bg-gray-500/20 text-gray-400', label: 'N/A' };
    if (score >= 85) return { color: 'bg-red-500/20 text-red-400', label: 'Kritis' };
    if (score >= 70) return { color: 'bg-orange-500/20 text-orange-400', label: 'Tinggi' };
    if (score >= 40) return { color: 'bg-yellow-500/20 text-yellow-400', label: 'Sedang' };
    return { color: 'bg-green-500/20 text-green-400', label: 'Rendah' };
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-gray-800/50 rounded-xl p-4 border border-gray-700">
        <h1 className="text-2xl font-bold text-white">Data Paket & Anggaran Pengadaan</h1>
        <p className="text-gray-400 text-sm mt-1">Rencana Umum Pengadaan (RUP) - Analisis paket dan anggaran</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-gray-800 rounded-xl p-4 border border-gray-700">
          <p className="text-gray-400 text-sm">Total Paket</p>
          <p className="text-2xl font-bold text-white">{stats?.total_packages || 0}</p>
        </div>
        <div className="bg-gray-800 rounded-xl p-4 border border-gray-700">
          <p className="text-gray-400 text-sm">Total Anggaran</p>
          <p className="text-2xl font-bold text-green-400">{formatCurrency(stats?.total_budget || 0)}</p>
        </div>
        <div className="bg-gray-800 rounded-xl p-4 border border-gray-700">
          <p className="text-gray-400 text-sm">Nilai Kontrak</p>
          <p className="text-2xl font-bold text-blue-400">{formatCurrency(stats?.total_contract_value || 0)}</p>
        </div>
        <div className="bg-gray-800 rounded-xl p-4 border border-gray-700">
          <p className="text-gray-400 text-sm">Rata-rata Risiko</p>
          <p className={`text-2xl font-bold ${(stats?.avg_risk_score || 0) >= 70 ? 'text-red-400' : (stats?.avg_risk_score || 0) >= 40 ? 'text-yellow-400' : 'text-green-400'}`}>
            {Math.round(stats?.avg_risk_score || 0)}%
          </p>
        </div>
      </div>

      {/* Filter */}
      <div className="bg-gray-800 rounded-xl p-4 border border-gray-700">
        <div className="flex gap-2 overflow-x-auto">
          <button
            onClick={() => setFilterStatus('all')}
            className={`px-3 py-1 rounded-lg text-sm ${filterStatus === 'all' ? 'bg-green-500/20 text-green-400' : 'bg-gray-700 text-gray-400'}`}
          >
            Semua
          </button>
          <button
            onClick={() => setFilterStatus('planning')}
            className={`px-3 py-1 rounded-lg text-sm ${filterStatus === 'planning' ? 'bg-blue-500/20 text-blue-400' : 'bg-gray-700 text-gray-400'}`}
          >
            Perencanaan
          </button>
          <button
            onClick={() => setFilterStatus('tendering')}
            className={`px-3 py-1 rounded-lg text-sm ${filterStatus === 'tendering' ? 'bg-yellow-500/20 text-yellow-400' : 'bg-gray-700 text-gray-400'}`}
          >
            Tender
          </button>
          <button
            onClick={() => setFilterStatus('contract')}
            className={`px-3 py-1 rounded-lg text-sm ${filterStatus === 'contract' ? 'bg-green-500/20 text-green-400' : 'bg-gray-700 text-gray-400'}`}
          >
            Kontrak
          </button>
        </div>
      </div>

      {/* Procurement Table */}
      <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-900">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-400">Nama Paket</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-400">Anggaran</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-400">Metode</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-400">Status</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-400">Risiko</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-400">Vendor</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-700">
              {packages.map((pkg) => {
                const status = getStatusBadge(pkg.status);
                const risk = getRiskBadge(pkg.risk_score);
                return (
                  <tr key={pkg.id} className="hover:bg-gray-700/30">
                    <td className="px-4 py-3 text-white">{pkg.package_name}</td>
                    <td className="px-4 py-3 text-gray-300">{formatCurrency(pkg.budget)}</td>
                    <td className="px-4 py-3 text-gray-300">{pkg.procurement_method}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 rounded-full text-xs ${status.color}`}>
                        {status.label}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      {pkg.risk_score && (
                        <span className={`px-2 py-1 rounded-full text-xs ${risk.color}`}>
                          {risk.label} ({pkg.risk_score}%)
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      {pkg.vendor_name ? (
                        <span className="text-blue-400 hover:underline cursor-pointer">
                          {pkg.vendor_name}
                        </span>
                      ) : (
                        <span className="text-gray-500">-</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default ProcurementDashboard;
