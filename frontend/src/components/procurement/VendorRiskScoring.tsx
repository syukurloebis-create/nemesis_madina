import React, { useEffect, useState } from 'react';
import { Building, AlertTriangle, CheckCircle, TrendingUp, Shield, FileText } from 'lucide-react';
import { procurementApi, VendorData } from '../../services/procurementApi';

export const VendorRiskScoring: React.FC = () => {
  const [vendors, setVendors] = useState<VendorData[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedVendor, setSelectedVendor] = useState<VendorData | null>(null);
  const [sortBy, setSortBy] = useState<'risk' | 'name' | 'contracts'>('risk');

  useEffect(() => {
    const fetchVendors = async () => {
      try {
        const response = await procurementApi.getSummary();
        // Data dummy untuk demo
        const dummyVendors: VendorData[] = [
          {
            id: '1',
            name: 'PT. Maju Jaya',
            type: 'vendor',
            riskScore: 92,
            address: 'Jl. Sudirman No. 123, Jakarta',
            taxId: '01.234.567.8-901.000',
            totalContracts: 15,
            totalValue: 2500000000,
            collusionScore: 88,
            contracts: []
          },
          {
            id: '2',
            name: 'CV. Karya Mandiri',
            type: 'vendor',
            riskScore: 88,
            address: 'Jl. Gatot Subroto No. 45, Jakarta',
            taxId: '02.345.678.9-012.000',
            totalContracts: 8,
            totalValue: 1200000000,
            collusionScore: 75,
            contracts: []
          },
          {
            id: '3',
            name: 'PT. Bangun Nusantara',
            type: 'vendor',
            riskScore: 78,
            address: 'Jl. Thamrin No. 67, Jakarta',
            taxId: '03.456.789.0-123.000',
            totalContracts: 12,
            totalValue: 1800000000,
            collusionScore: 65,
            contracts: []
          }
        ];
        setVendors(dummyVendors);
      } catch (err) {
        console.error('Failed to fetch vendors:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchVendors();
  }, []);

  const getRiskLevel = (score: number) => {
    if (score >= 70) return { level: 'Tinggi', color: 'red', icon: AlertTriangle };
    if (score >= 40) return { level: 'Sedang', color: 'yellow', icon: Shield };
    return { level: 'Rendah', color: 'green', icon: CheckCircle };
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const sortedVendors = [...vendors].sort((a, b) => {
    if (sortBy === 'risk') return b.riskScore - a.riskScore;
    if (sortBy === 'name') return a.name.localeCompare(b.name);
    return b.totalContracts - a.totalContracts;
  });

  if (loading) {
    return (
      <div className="flex justify-center py-8">
        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-cyan-500"></div>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Vendor List */}
      <div className="lg:col-span-2 bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
        <div className="px-4 py-3 border-b border-gray-700 flex justify-between items-center">
          <h3 className="font-semibold text-white">Daftar Vendor</h3>
          <div className="flex space-x-2">
            <button
              onClick={() => setSortBy('risk')}
              className={`text-xs px-2 py-1 rounded ${sortBy === 'risk' ? 'bg-cyan-500/20 text-cyan-400' : 'text-gray-500'}`}
            >
              Sort by Risk
            </button>
            <button
              onClick={() => setSortBy('name')}
              className={`text-xs px-2 py-1 rounded ${sortBy === 'name' ? 'bg-cyan-500/20 text-cyan-400' : 'text-gray-500'}`}
            >
              Sort by Name
            </button>
          </div>
        </div>
        
        <div className="divide-y divide-gray-700 max-h-96 overflow-y-auto">
          {sortedVendors.map((vendor) => {
            const risk = getRiskLevel(vendor.riskScore);
            const RiskIcon = risk.icon;
            
            return (
              <div
                key={vendor.id}
                className={`p-4 cursor-pointer transition hover:bg-gray-700/30 ${
                  selectedVendor?.id === vendor.id ? 'bg-cyan-500/10' : ''
                }`}
                onClick={() => setSelectedVendor(vendor)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3">
                    <Building className="w-5 h-5 text-cyan-400 mt-0.5" />
                    <div>
                      <h4 className="font-medium text-white">{vendor.name}</h4>
                      <p className="text-xs text-gray-500">{vendor.address}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className={`text-xs px-2 py-0.5 rounded bg-${risk.color}-900 text-${risk.color}-300 flex items-center`}>
                      <RiskIcon className="w-3 h-3 mr-1" />
                      Risiko {risk.level}
                    </div>
                    <div className="text-xs text-gray-500 mt-1">{vendor.riskScore}%</div>
                  </div>
                </div>
                
                <div className="mt-3 flex items-center space-x-4 text-xs">
                  <span className="text-gray-500">NPWP: {vendor.taxId}</span>
                  <span className="text-gray-500">Kontrak: {vendor.totalContracts}</span>
                  <span className="text-gray-500">Nilai: {formatCurrency(vendor.totalValue)}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Vendor Detail */}
      <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
        {selectedVendor ? (
          <>
            <div className="px-4 py-3 border-b border-gray-700 bg-cyan-500/10">
              <h3 className="font-semibold text-white">Profil Risiko</h3>
              <p className="text-xs text-cyan-400 truncate">{selectedVendor.name}</p>
            </div>
            
            <div className="p-4 space-y-4">
              {/* Risk Score Meter */}
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-400">Skor Risiko</span>
                  <span className="text-white font-bold">{selectedVendor.riskScore}%</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full ${
                      selectedVendor.riskScore > 70 ? 'bg-red-500' :
                      selectedVendor.riskScore > 40 ? 'bg-yellow-500' : 'bg-green-500'
                    }`}
                    style={{ width: `${selectedVendor.riskScore}%` }}
                  />
                </div>
              </div>
              
              {/* Collusion Score */}
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-400">Skor Kolusi</span>
                  <span className="text-white font-bold">{selectedVendor.collusionScore}%</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div 
                    className="bg-purple-500 h-2 rounded-full"
                    style={{ width: `${selectedVendor.collusionScore}%` }}
                  />
                </div>
              </div>
              
              {/* Info */}
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-500">Total Kontrak:</span>
                  <span className="text-white">{selectedVendor.totalContracts}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Nilai Total:</span>
                  <span className="text-yellow-400">{formatCurrency(selectedVendor.totalValue)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Rata-rata per Kontrak:</span>
                  <span className="text-white">{formatCurrency(selectedVendor.totalValue / selectedVendor.totalContracts)}</span>
                </div>
              </div>
              
              {/* Risk Factors */}
              <div className="pt-3 border-t border-gray-700">
                <h4 className="text-sm font-medium text-gray-300 mb-2">Faktor Risiko</h4>
                <div className="space-y-2">
                  {selectedVendor.riskScore > 70 && (
                    <div className="flex items-center space-x-2 text-xs text-red-400">
                      <AlertTriangle className="w-3 h-3" />
                      <span>Skor risiko melebihi ambang batas</span>
                    </div>
                  )}
                  {selectedVendor.collusionScore > 70 && (
                    <div className="flex items-center space-x-2 text-xs text-purple-400">
                      <TrendingUp className="w-3 h-3" />
                      <span>Pola kolusi terdeteksi</span>
                    </div>
                  )}
                  <div className="flex items-center space-x-2 text-xs text-yellow-400">
                    <FileText className="w-3 h-3" />
                    <span>Perlu audit mendalam</span>
                  </div>
                </div>
              </div>
              
              <button className="w-full mt-2 px-3 py-2 bg-cyan-500/20 text-cyan-400 rounded hover:bg-cyan-500/30 transition text-sm">
                Audit Vendor
              </button>
            </div>
          </>
        ) : (
          <div className="flex items-center justify-center h-full min-h-[300px] text-gray-500">
            <div className="text-center">
              <Building className="w-12 h-12 mx-auto mb-2 opacity-50" />
              <p>Pilih vendor untuk melihat profil risiko</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
