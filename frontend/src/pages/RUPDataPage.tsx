import React, { useState, useEffect } from 'react';

const RUPDataPage: React.FC = () => {
  const [data, setData] = useState<any[]>([]);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const [dataRes, statsRes] = await Promise.all([
          fetch(`/api/rup-data?page=${page}&limit=20`),
          fetch('/api/rup-stats')
        ]);
        const dataJson = await dataRes.json();
        const statsJson = await statsRes.json();
        setData(dataJson.data || []);
        setTotalPages(dataJson.total_pages || 1);
        setStats(statsJson);
      } catch (error) {
        console.error('Error:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
    
    window.addEventListener('rup-data-updated', fetchData);
    return () => window.removeEventListener('rup-data-updated', fetchData);
  }, [page]);

  const formatPagu = (pagu: number) => {
    return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(pagu);
  };

  if (loading) return <div className="p-6">Loading...</div>;

  return (
    <div className="p-6 ml-64">
      <h1 className="text-2xl font-bold mb-6">📦 Data RUP Mandailing Natal</h1>
      
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-4"><div className="text-sm text-gray-500">Total Paket</div><div className="text-2xl font-bold">{stats.total}</div></div>
          <div className="bg-white rounded-lg shadow p-4"><div className="text-sm text-gray-500">Total Pagu</div><div className="text-2xl font-bold text-green-600">{formatPagu(stats.total_pagu)}</div></div>
          {stats.by_year?.map((year: any) => (
            <div key={year.tahun} className="bg-white rounded-lg shadow p-4"><div className="text-sm text-gray-500">Tahun {year.tahun}</div><div className="text-xl font-bold">{year.count} paket</div></div>
          ))}
        </div>
      )}
      
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50"><tr><th className="px-6 py-3 text-left">ID</th><th className="px-6 py-3 text-left">Nama Paket</th><th className="px-6 py-3 text-left">Pagu</th><th className="px-6 py-3 text-left">Jenis</th><th className="px-6 py-3 text-left">Tahun</th><th className="px-6 py-3 text-left">Instansi</th></tr></thead>
          <tbody>{data.map((item: any) => (<tr key={item.nomor_id} className="border-b hover:bg-gray-50"><td className="px-6 py-4">{item.nomor_id}</td><td className="px-6 py-4">{item.nama_paket?.substring(0, 60)}</td><td className="px-6 py-4">{formatPagu(item.pagu)}</td><td className="px-6 py-4"><span className="px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800">{item.jenis}</span></td><td className="px-6 py-4">{item.tahun}</td><td className="px-6 py-4">{item.instansi?.substring(0, 40)}</td></tr>))}</tbody>
        </table>
      </div>
      
      {totalPages > 1 && (<div className="flex justify-center gap-2 mt-4"><button onClick={() => setPage(p => Math.max(1, p-1))} disabled={page === 1} className="px-3 py-1 bg-gray-200 rounded disabled:opacity-50">Prev</button><span className="px-3 py-1">Page {page} of {totalPages}</span><button onClick={() => setPage(p => Math.min(totalPages, p+1))} disabled={page === totalPages} className="px-3 py-1 bg-gray-200 rounded disabled:opacity-50">Next</button></div>)}
    </div>
  );
};

export default RUPDataPage;
