import React, { useEffect, useState } from 'react';
import apiService, { getRUPStats, getRUPData, getRUPTahun, getRUPStatus, exportRUP } from '../../services/api';

interface RUPRecord {
  id: number;
  nomor_id: string;
  nama_paket: string;
  pagu: number;
  pagu_formatted: string;
  jenis: string;
  tahun: number;
  metode: string;
  instansi: string;
  status: string;
}

interface RUPStats {
  total_paket: number;
  total_pagu: number;
  total_pagu_formatted: string;
  tahun_2025: number;
  tahun_2026: number;
  selesai: number;
  berjalan: number;
  dalam_proses: number;
}

export default function RUPData() {
  const [rups, setRups] = useState<RUPRecord[]>([]);
  const [stats, setStats] = useState<RUPStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [filterYear, setFilterYear] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [years, setYears] = useState<number[]>([]);
  const [statuses, setStatuses] = useState<string[]>([]);

  useEffect(() => {
    loadData();
    loadFilters();
  }, []);

  useEffect(() => {
    loadData();
  }, [filterYear, filterStatus, search]);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const statsRes = await getRUPStats();
      console.log('RUP Stats:', statsRes.data);
      setStats(statsRes.data);

      const params: any = { limit: 100 };
      if (filterYear) params.tahun = parseInt(filterYear);
      if (filterStatus) params.status = filterStatus;
      if (search) params.search = search;

      const dataRes = await getRUPData(params);
      console.log('RUP Data Response:', dataRes.data);
      
      let records: RUPRecord[] = [];
      
      if (dataRes.data) {
        if (Array.isArray(dataRes.data)) {
          records = dataRes.data;
        } else if (dataRes.data.data && Array.isArray(dataRes.data.data)) {
          records = dataRes.data.data;
        }
      }
      
      setRups(records);
    } catch (err: any) {
      console.error('Failed to load RUP data:', err);
      setError(err.message || 'Gagal memuat data RUP');
      setRups([]);
    } finally {
      setLoading(false);
    }
  };

  const loadFilters = async () => {
    try {
      const [yearsRes, statusesRes] = await Promise.all([
        getRUPTahun(),
        getRUPStatus()
      ]);
      setYears(yearsRes.data?.tahun || []);
      setStatuses(statusesRes.data?.status || []);
    } catch (err) {
      console.error('Failed to load filters:', err);
    }
  };

  const handleSearch = () => {
    loadData();
  };

  const handleExport = async () => {
    try {
      const params: any = {};
      if (filterYear) params.tahun = parseInt(filterYear);
      if (filterStatus) params.status = filterStatus;
      if (search) params.search = search;
      
      const response = await exportRUP(params);
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `rup_export_${new Date().toISOString().slice(0, 19)}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Export failed:', err);
      alert('Gagal mengexport data');
    }
  };

  const formatRupiah = (value: number) => {
    if (!value) return 'Rp0';
    return `Rp${value.toLocaleString('id-ID')}`;
  };

  if (loading) {
    return <div className="p-6"><div className="text-center py-12 text-gray-400">Memuat data RUP...</div></div>;
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-900/20 border border-red-500 rounded-lg p-6">
          <p className="text-red-400 text-lg">⚠️ Error Memuat Data</p>
          <p className="text-gray-400 mt-2">{error}</p>
          <button onClick={loadData} className="mt-4 px-4 py-2 bg-cyan-600 rounded hover:bg-cyan-500">Coba Lagi</button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold text-cyan-400 mb-2">Data RUP Mandailing Natal</h1>
      <p className="text-gray-400 mb-6">Rencana Umum Pengadaan Kabupaten Mandailing Natal</p>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
        <div className="bg-gray-800 rounded-lg p-4 text-center border border-gray-700">
          <div className="text-2xl font-bold text-cyan-400">{stats?.total_paket?.toLocaleString() || 0}</div>
          <div className="text-gray-400 text-sm">Total Paket</div>
        </div>

        <div className="bg-gray-800 rounded-lg p-4 text-center border border-gray-700 col-span-1 sm:col-span-1 md:col-span-1 lg:col-span-2">
          <div className="text-xl font-bold text-green-400">{formatRupiah(stats?.total_pagu || 0)}</div>
          <div className="text-gray-400 text-sm">Total Pagu</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 text-center border border-gray-700">
          <div className="text-2xl font-bold text-yellow-400">{stats?.tahun_2025?.toLocaleString() || 0}</div>
          <div className="text-gray-400 text-sm">Tahun 2025</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 text-center border border-gray-700">
          <div className="text-2xl font-bold text-orange-400">{stats?.tahun_2026?.toLocaleString() || 0}</div>
          <div className="text-gray-400 text-sm">Tahun 2026</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 text-center border border-gray-700">
          <div className="text-2xl font-bold text-green-400">{stats?.selesai || 0}</div>
          <div className="text-gray-400 text-sm">Selesai</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 text-center border border-gray-700">
          <div className="text-2xl font-bold text-blue-400">{stats?.berjalan || 0}</div>
          <div className="text-gray-400 text-sm">Berjalan</div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-gray-800 rounded-lg p-4 mb-6">
        <div className="flex flex-wrap gap-4 items-end">
          <div className="flex-1 min-w-[200px]">
            <label className="block text-gray-400 text-sm mb-1">Cari paket, ID, atau vendor...</label>
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              className="w-full px-3 py-2 bg-gray-700 rounded text-white"
              placeholder="Cari paket, ID, atau vendor..."
            />
          </div>
          <div>
            <label className="block text-gray-400 text-sm mb-1">Tahun</label>
            <select
              value={filterYear}
              onChange={(e) => setFilterYear(e.target.value)}
              className="px-3 py-2 bg-gray-700 rounded text-white"
            >
              <option value="">Semua Tahun</option>
              {years.map(year => (
                <option key={year} value={year}>{year}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-gray-400 text-sm mb-1">Status</label>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-3 py-2 bg-gray-700 rounded text-white"
            >
              <option value="">Semua Status</option>
              {statuses.map(status => (
                <option key={status} value={status}>{status}</option>
              ))}
            </select>
          </div>
          <button onClick={handleSearch} className="px-4 py-2 bg-cyan-600 rounded hover:bg-cyan-500">Cari</button>
          <button onClick={handleExport} className="px-4 py-2 bg-green-600 rounded hover:bg-green-500">Export Excel</button>
        </div>
      </div>

      {/* Data Table */}
      <div className="bg-gray-800 rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-700">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-300">ID</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-300">Nama Paket</th>
                <th className="px-4 py-3 text-left text-sm font-medium text-gray-300">Instansi</th>
                <th className="px-4 py-3 text-right text-sm font-medium text-gray-300">Pagu</th>
                <th className="px-4 py-3 text-center text-sm font-medium text-gray-300">Tahun</th>
                <th className="px-4 py-3 text-center text-sm font-medium text-gray-300">Status</th>
              </tr>
            </thead>
            <tbody>
              {rups.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-4 py-8 text-center text-gray-500">Tidak ada data RUP</td>
                </tr>
              ) : (
                rups.map((rup) => (
                  <tr key={rup.id} className="border-t border-gray-700 hover:bg-gray-700/50">
                    <td className="px-4 py-3 text-sm text-gray-300">{rup.nomor_id || rup.id}</td>
                    <td className="px-4 py-3 text-sm text-gray-300">{rup.nama_paket?.substring(0, 60)}...</td>
                    <td className="px-4 py-3 text-sm text-gray-300">{rup.instansi || '-'}</td>
                    <td className="px-4 py-3 text-sm text-right text-green-400">{formatRupiah(rup.pagu)}</td>
                    <td className="px-4 py-3 text-sm text-center text-gray-300">{rup.tahun || '-'}</td>
                    <td className="px-4 py-3 text-sm text-center">
                      <span className={`px-2 py-1 rounded text-xs ${
                        rup.status === 'Selesai' ? 'bg-green-900/50 text-green-400' :
                        rup.status === 'Berjalan' ? 'bg-blue-900/50 text-blue-400' :
                        'bg-yellow-900/50 text-yellow-400'
                      }`}>
                        {rup.status || 'Dalam Proses'}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      <div className="mt-4 text-right text-gray-500 text-sm">
        Menampilkan {rups.length} dari {stats?.total_paket?.toLocaleString() || 0} data
      </div>
    </div>
  );
}
