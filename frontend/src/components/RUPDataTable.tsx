// src/components/RUPDataTable.tsx
import React, { useState, useEffect } from 'react';

interface RUPData {
  id: number;
  nomor_id: string;
  nama_paket: string;
  pagu: number;
  jenis: string;
  tahun: number;
  kategori: string;
  metode: string;
  bulan: string;
  lokasi: string;
  instansi: string;
}

const RUPDataTable: React.FC = () => {
  const [data, setData] = useState<RUPData[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Fetch data dengan timeout dan error handling
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 30000);
      
      const [dataRes, statsRes] = await Promise.all([
        fetch(`/api/rup-data?page=${page}&limit=10`, { signal: controller.signal }),
        fetch('/api/rup-stats', { signal: controller.signal }),
      ]);
      
      clearTimeout(timeoutId);
      
      if (!dataRes.ok) {
        throw new Error(`HTTP ${dataRes.status}: ${dataRes.statusText}`);
      }
      
      if (!statsRes.ok) {
        throw new Error(`HTTP ${statsRes.status}: ${statsRes.statusText}`);
      }
      
      // Parse JSON dengan aman
      let dataJson, statsJson;
      try {
        dataJson = await dataRes.json();
        statsJson = await statsRes.json();
      } catch (parseError) {
        throw new Error('Gagal memparse response dari server');
      }
      
      setData(dataJson.data || []);
      setTotalPages(dataJson.total_pages || 1);
      setStats(statsJson);
      
    } catch (error: any) {
      console.error('Error fetching RUP data:', error);
      if (error.name === 'AbortError') {
        setError('Request timeout. Server mungkin lambat merespon.');
      } else {
        setError(error.message || 'Gagal memuat data. Pastikan backend server berjalan di port 8000.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    
    const handleUpdate = () => {
      fetchData();
    };
    
    window.addEventListener('rup-data-updated', handleUpdate);
    return () => window.removeEventListener('rup-data-updated', handleUpdate);
  }, [page]);

  const formatPagu = (pagu: number) => {
    if (!pagu && pagu !== 0) return 'Rp 0';
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(pagu);
  };

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="text-center">
          <div className="text-red-600 text-lg mb-2">⚠️ Error</div>
          <p className="text-gray-600 mb-4">{error}</p>
          <button 
            onClick={fetchData}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Coba Lagi
          </button>
        </div>
      </div>
    );
  }

  if (loading && data.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="text-center text-gray-500">
          <div className="animate-spin text-2xl mb-2">⏳</div>
          Loading data RUP...
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">
          📋 Data RUP Terupload
        </h2>
        {stats && (
          <div className="flex gap-4 mt-2 text-sm flex-wrap">
            <span className="text-gray-600">
              Total Paket: <strong className="text-gray-900">{stats.total?.toLocaleString() || 0}</strong>
            </span>
            <span className="text-gray-600">
              Total Pagu: <strong className="text-gray-900">{formatPagu(stats.total_pagu)}</strong>
            </span>
            {stats.by_year?.map((year: any) => (
              <span key={year.tahun} className="text-gray-600">
                {year.tahun}: <strong className="text-gray-900">{year.count.toLocaleString()}</strong>
              </span>
            ))}
          </div>
        )}
      </div>
      
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Nama Paket</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Pagu</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Jenis</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tahun</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Instansi</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {data.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-6 py-8 text-center text-gray-500">
                  Belum ada data. Upload file CSV/Excel untuk mulai.
                 </td>
               </tr>
            ) : (
              data.map((item) => (
                <tr key={item.nomor_id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm text-gray-500">{item.nomor_id}</td>
                  <td className="px-6 py-4 text-sm text-gray-900 max-w-md truncate" title={item.nama_paket}>
                    {item.nama_paket?.length > 60 ? item.nama_paket.substring(0, 60) + '...' : item.nama_paket}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">{formatPagu(item.pagu)}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      item.jenis === 'Barang' ? 'bg-blue-100 text-blue-800' :
                      item.jenis === 'Pekerjaan Konstruksi' ? 'bg-orange-100 text-orange-800' :
                      item.jenis === 'Jasa Konsultansi' ? 'bg-purple-100 text-purple-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {item.jenis}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">{item.tahun}</td>
                  <td className="px-6 py-4 text-sm text-gray-500 max-w-xs truncate" title={item.instansi}>
                    {item.instansi?.length > 40 ? item.instansi.substring(0, 40) + '...' : item.instansi}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
      
      {/* Pagination */}
      {totalPages > 1 && (
        <div className="px-6 py-4 border-t border-gray-200 flex justify-between items-center">
          <button
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
            className="px-3 py-1 text-sm bg-gray-100 rounded disabled:opacity-50 hover:bg-gray-200"
          >
            Previous
          </button>
          <span className="text-sm text-gray-600">
            Page {page} of {totalPages}
          </span>
          <button
            onClick={() => setPage(p => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
            className="px-3 py-1 text-sm bg-gray-100 rounded disabled:opacity-50 hover:bg-gray-200"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
};

export default RUPDataTable;