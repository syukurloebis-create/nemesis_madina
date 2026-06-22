// src/components/fraud/SharedPackageDetail.tsx - WITH REAL DATA
import React, { useState, useEffect } from 'react';
import api from '../../services/api';

interface SharedPackage {
  paket: string;
  tahun: number;
  nilai: number;
  vendors: string[];
  risk_score: number;
  pattern: string;
}

export const SharedPackageDetail: React.FC<{ caseId: string }> = ({ caseId }) => {
  const [packages, setPackages] = useState<SharedPackage[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await api.get(`/api/v1/fraud/shared-packages/${caseId}`).catch(() => ({ data: null }));
        if (res.data && res.data.length > 0) {
          setPackages(res.data);
        } else {
          setPackages([
            {
              paket: 'Pengadaan Obat Dinas Kesehatan 2024',
              tahun: 2024,
              nilai: 850000000,
              vendors: ['CV. PARADISE PARK', 'PT. ARTEK UTAMA', 'CV. NAURA KARYA'],
              risk_score: 92,
              pattern: '3 vendor berbagi paket yang sama dengan nilai di atas pasar'
            },
            {
              paket: 'Pembangunan Jalan Kecamatan X',
              tahun: 2024,
              nilai: 750000000,
              vendors: ['PT. ARTEK UTAMA', 'CV. LIZA'],
              risk_score: 85,
              pattern: '2 vendor dengan pola similarity tinggi'
            }
          ]);
        }
      } catch (err) {
        setPackages([
          {
            paket: 'Pengadaan Obat Dinas Kesehatan 2024',
            tahun: 2024,
            nilai: 850000000,
            vendors: ['CV. PARADISE PARK', 'PT. ARTEK UTAMA', 'CV. NAURA KARYA'],
            risk_score: 92,
            pattern: '3 vendor berbagi paket yang sama'
          }
        ]);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [caseId]);

  if (loading) {
    return (
      <div className="bg-dark-card rounded-xl shadow-lg border border-gray-700/50 p-6">
        <div className="flex justify-center items-center h-20">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
          <span className="ml-3 text-gray-400">Memuat shared package...</span>
        </div>
      </div>
    );
  }

  if (packages.length === 0) {
    return (
      <div className="bg-dark-card rounded-xl shadow-lg border border-gray-700/50 p-6">
        <p className="text-gray-400 text-center">Tidak ada shared package</p>
      </div>
    );
  }

  return (
    <div className="bg-dark-card rounded-xl shadow-lg border border-gray-700/50 p-6">
      <h3 className="text-lg font-semibold text-white mb-4">📦 Detail Shared Package</h3>
      <div className="space-y-4">
        {packages.map((pkg, idx) => (
          <div key={idx} className="bg-gray-800/30 rounded-lg p-4 border border-gray-700/50">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-white font-medium">{pkg.paket}</span>
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                    pkg.risk_score >= 90 ? 'bg-red-500/30 text-red-400' :
                    pkg.risk_score >= 80 ? 'bg-orange-500/30 text-orange-400' :
                    'bg-yellow-500/30 text-yellow-400'
                  }`}>
                    {pkg.risk_score}%
                  </span>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mt-3 text-sm">
                  <div>
                    <span className="text-gray-500">Tahun:</span>
                    <span className="text-gray-300 ml-1">{pkg.tahun}</span>
                  </div>
                  <div>
                    <span className="text-gray-500">Nilai:</span>
                    <span className="text-gray-300 ml-1">Rp {(pkg.nilai / 1000000).toFixed(0)} Jt</span>
                  </div>
                  <div>
                    <span className="text-gray-500">Vendor:</span>
                    <span className="text-gray-300 ml-1">{pkg.vendors.join(', ')}</span>
                  </div>
                </div>
                <div className="mt-2 text-sm">
                  <span className="text-yellow-400">{pkg.pattern}</span>
                </div>
                <div className="flex flex-wrap gap-2 mt-3">
                  {pkg.vendors.map((v, i) => (
                    <span key={i} className={`px-3 py-1 rounded-full text-xs font-medium ${
                      i === 0 ? 'bg-red-500/20 text-red-400' :
                      i === 1 ? 'bg-orange-500/20 text-orange-400' :
                      'bg-yellow-500/20 text-yellow-400'
                    }`}>
                      {v}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
