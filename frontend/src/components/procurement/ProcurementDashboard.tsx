import React, { useEffect, useState } from 'react';
import { 
  ShoppingBag, 
  Building, 
  FileText, 
  AlertTriangle, 
  TrendingUp,
  Shield,
  DollarSign,
  Users,
  Activity,
  ExternalLink
} from 'lucide-react';
import { procurementApi, ProcurementSummary, CollusionPattern } from '../../services/procurementApi';

export const ProcurementDashboard: React.FC = () => {
  const [summary, setSummary] = useState<ProcurementSummary | null>(null);
  const [collusionPatterns, setCollusionPatterns] = useState<CollusionPattern[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedTab, setSelectedTab] = useState<'overview' | 'collusion' | 'vendors'>('overview');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [summaryData, patternsData] = await Promise.all([
          procurementApi.getSummary(),
          procurementApi.getCollusionPatterns()
        ]);
        setSummary(summaryData);
        setCollusionPatterns(patternsData);
      } catch (err) {
        console.error('Failed to fetch procurement data:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-900 text-red-300 border-red-700';
      case 'high': return 'bg-orange-900 text-orange-300 border-orange-700';
      case 'medium': return 'bg-yellow-900 text-yellow-300 border-yellow-700';
      default: return 'bg-gray-700 text-gray-300 border-gray-600';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-500 mx-auto"></div>
          <p className="mt-4 text-gray-400">Memuat data pengadaan...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white">Intelijen Pengadaan</h1>
        <p className="text-gray-400 mt-1">
          Deteksi anomali, kolusi, dan risiko dalam proses pengadaan
        </p>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="flex items-center justify-between">
            <ShoppingBag className="w-5 h-5 text-cyan-400" />
            <span className="text-2xl font-bold text-white">{summary?.totalCases || 0}</span>
          </div>
          <div className="text-xs text-gray-500 mt-1">Total Kasus</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="flex items-center justify-between">
            <Building className="w-5 h-5 text-yellow-400" />
            <span className="text-2xl font-bold text-white">{summary?.totalVendors || 0}</span>
          </div>
          <div className="text-xs text-gray-500 mt-1">Total Vendor</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="flex items-center justify-between">
            <DollarSign className="w-5 h-5 text-green-400" />
            <span className="text-lg font-bold text-white">{formatCurrency(summary?.totalValue || 0)}</span>
          </div>
          <div className="text-xs text-gray-500 mt-1">Nilai Pengadaan</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="flex items-center justify-between">
            <AlertTriangle className="w-5 h-5 text-red-400" />
            <span className="text-2xl font-bold text-white">{summary?.highRiskVendors || 0}</span>
          </div>
          <div className="text-xs text-gray-500 mt-1">Vendor Risiko Tinggi</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="flex items-center justify-between">
            <Activity className="w-5 h-5 text-purple-400" />
            <span className="text-2xl font-bold text-white">{collusionPatterns.length}</span>
          </div>
          <div className="text-xs text-gray-500 mt-1">Pola Kolusi</div>
        </div>
        <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
          <div className="flex items-center justify-between">
            <Shield className="w-5 h-5 text-green-400" />
            <span className="text-2xl font-bold text-white">{summary?.integrityScore || 0}%</span>
          </div>
          <div className="text-xs text-gray-500 mt-1">Skor Integritas</div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-2 border-b border-gray-700">
        <button
          onClick={() => setSelectedTab('overview')}
          className={`px-4 py-2 text-sm font-medium rounded-t-lg transition ${
            selectedTab === 'overview'
              ? 'bg-cyan-500/20 text-cyan-400 border-b-2 border-cyan-500'
              : 'text-gray-400 hover:text-gray-300'
          }`}
        >
          📊 Ikhtisar Pengadaan
        </button>
        <button
          onClick={() => setSelectedTab('collusion')}
          className={`px-4 py-2 text-sm font-medium rounded-t-lg transition ${
            selectedTab === 'collusion'
              ? 'bg-cyan-500/20 text-cyan-400 border-b-2 border-cyan-500'
              : 'text-gray-400 hover:text-gray-300'
          }`}
        >
          🔗 Pola Kolusi ({collusionPatterns.length})
        </button>
        <button
          onClick={() => setSelectedTab('vendors')}
          className={`px-4 py-2 text-sm font-medium rounded-t-lg transition ${
            selectedTab === 'vendors'
              ? 'bg-cyan-500/20 text-cyan-400 border-b-2 border-cyan-500'
              : 'text-gray-400 hover:text-gray-300'
          }`}
        >
          🏢 Vendor Berisiko
        </button>
      </div>

      {/* Tab Content */}
      {selectedTab === 'overview' && (
        <div className="space-y-6">
          {/* Trend Chart */}
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <h3 className="text-sm font-medium text-gray-300 mb-3">Tren Nilai Pengadaan</h3>
            <div className="h-48 flex items-end space-x-2">
              {(summary?.monthlyTrend || []).map((item, idx) => (
                <div key={idx} className="flex-1 flex flex-col items-center">
                  <div 
                    className="w-full bg-cyan-500 rounded-t"
                    style={{ height: `${(item.value / 2000000000) * 100}%`, minHeight: '4px' }}
                  />
                  <span className="text-xs text-gray-500 mt-2">{item.month}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 hover:border-cyan-500/50 transition">
              <h4 className="font-medium text-white mb-2">Analisis Risiko Vendor</h4>
              <p className="text-xs text-gray-400">Identifikasi vendor dengan pola mencurigakan</p>
              <button className="mt-3 text-xs text-cyan-400 flex items-center">
                Analisis <ExternalLink className="w-3 h-3 ml-1" />
              </button>
            </div>
            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 hover:border-cyan-500/50 transition">
              <h4 className="font-medium text-white mb-2">Deteksi Kolusi</h4>
              <p className="text-xs text-gray-400">Scan pola kolusi antar vendor</p>
              <button className="mt-3 text-xs text-cyan-400 flex items-center">
              Deteksi <ExternalLink className="w-3 h-3 ml-1" />
              </button>
            </div>
            <div className="bg-gray-800 rounded-lg p-4 border border-gray-700 hover:border-cyan-500/50 transition">
              <h4 className="font-medium text-white mb-2">Laporan Pengadaan</h4>
              <p className="text-xs text-gray-400">Generate laporan audit pengadaan</p>
              <button className="mt-3 text-xs text-cyan-400 flex items-center">
                Generate <ExternalLink className="w-3 h-3 ml-1" />
              </button>
            </div>
          </div>
        </div>
      )}

      {selectedTab === 'collusion' && (
        <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
          <div className="divide-y divide-gray-700">
            {collusionPatterns.map((pattern) => (
              <div key={pattern.id} className="p-4 hover:bg-gray-700/30 transition">
                <div className="flex items-center justify-between flex-wrap gap-2">
                  <div className="flex items-center space-x-2">
                    <span className={`text-xs px-2 py-0.5 rounded ${getSeverityColor(pattern.severity)}`}>
                      {pattern.severity === 'critical' ? 'KRITIS' : 
                       pattern.severity === 'high' ? 'TINGGI' : 
                       pattern.severity === 'medium' ? 'SEDANG' : 'RENDAH'}
                    </span>
                    <h4 className="font-medium text-white">{pattern.type}</h4>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-xs text-gray-500">Keyakinan:</span>
                    <div className="w-24 bg-gray-700 rounded-full h-1.5">
                      <div 
                        className="bg-cyan-500 h-1.5 rounded-full" 
                        style={{ width: `${pattern.confidence}%` }}
                      />
                    </div>
                    <span className="text-xs text-cyan-400">{pattern.confidence}%</span>
                  </div>
                </div>
                
                <p className="text-sm text-gray-400 mt-2">{pattern.description}</p>
                
                <div className="mt-3">
                  <p className="text-xs text-gray-500 mb-1">Entitas yang terlibat:</p>
                  <div className="flex flex-wrap gap-2">
                    {pattern.entities.map((entity, idx) => (
                      <span key={idx} className="text-xs bg-gray-700 px-2 py-1 rounded">
                        🏢 {entity}
                      </span>
                    ))}
                  </div>
                </div>
                
                <div className="mt-3 text-xs text-gray-500">
                  Terdeteksi: {new Date(pattern.detectedAt).toLocaleString('id-ID')}
                  {pattern.caseIds.length > 0 && ` • Terkait ${pattern.caseIds.length} kasus`}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {selectedTab === 'vendors' && (
        <div className="bg-gray-800 rounded-lg border border-gray-700 p-4 text-center text-gray-500">
          <Building className="w-12 h-12 mx-auto mb-2 opacity-50" />
          <p>Daftar vendor akan ditampilkan di sini</p>
          <p className="text-xs mt-1">Integrasikan dengan endpoint /vendors untuk data lengkap</p>
        </div>
      )}
    </div>
  );
};
