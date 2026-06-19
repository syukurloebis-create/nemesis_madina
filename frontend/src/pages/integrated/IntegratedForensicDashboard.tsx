import React, { useEffect, useState } from 'react';
import { WorkspaceLayout } from '../../WorkspaceLayout';
import { api } from '../../services/api';
import { procurementApi } from '../../services/procurementApi';
import { useAuthStore } from '../../stores/authStore';
import { 
  ShoppingBag, Building, FileText, AlertTriangle, Shield, 
  TrendingUp, Users, DollarSign, Calendar, Eye, Download,
  ChevronDown, ChevronUp, Search, Filter, ExternalLink
} from 'lucide-react';

interface Case {
  id: string;
  title: string;
  description: string;
  status: string;
  priority: string;
  created_at: string;
  assigned_to: string | null;
  procurement_value?: number;
  vendor_count?: number;
  anomaly_score?: number;
}

interface Entity {
  id: string;
  name: string;
  entity_type: string;
  risk_score: number;
  confidence: number;
  first_seen: string;
  total_cases?: number;
  total_value?: number;
}

interface ProcurementSummary {
  totalCases: number;
  totalVendors: number;
  totalContracts: number;
  totalValue: number;
  highRiskVendors: number;
  collusionPatterns: number;
  integrityScore: number;
}

export default function IntegratedForensicDashboard() {
  const { token } = useAuthStore();
  const [cases, setCases] = useState<Case[]>([]);
  const [entities, setEntities] = useState<Entity[]>([]);
  const [procurementSummary, setProcurementSummary] = useState<ProcurementSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedTab, setSelectedTab] = useState<'cases' | 'entities' | 'procurement'>('cases');
  const [searchTerm, setSearchTerm] = useState('');
  const [expandedCase, setExpandedCase] = useState<string | null>(null);
  const [selectedEntity, setSelectedEntity] = useState<Entity | null>(null);

  useEffect(() => {
    const fetchAllData = async () => {
      if (!token) return;
      try {
        const [casesRes, entitiesRes, summaryRes] = await Promise.all([
          api.getCases(),
          api.getEntities(''),
          procurementApi.getSummary()
        ]);
        
        const casesData = casesRes.data || casesRes || [];
        setCases(casesData);
        setEntities(entitiesRes || []);
        setProcurementSummary(summaryRes);
      } catch (err) {
        console.error('Failed to fetch data:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchAllData();
  }, [token]);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const getStatusBadge = (status: string) => {
    const badges: Record<string, string> = {
      'OPEN': 'bg-green-900 text-green-300',
      'INVESTIGATING': 'bg-blue-900 text-blue-300',
      'RESOLVED': 'bg-gray-700 text-gray-300',
      'CLOSED': 'bg-gray-800 text-gray-500'
    };
    return badges[status] || 'bg-gray-700 text-gray-300';
  };

  const getPriorityBadge = (priority: string) => {
    const badges: Record<string, string> = {
      'CRITICAL': 'bg-red-900 text-red-300',
      'HIGH': 'bg-orange-900 text-orange-300',
      'MEDIUM': 'bg-yellow-900 text-yellow-300',
      'LOW': 'bg-green-900 text-green-300'
    };
    return badges[priority] || 'bg-gray-700 text-gray-300';
  };

  const getRiskBadge = (score: number) => {
    if (score >= 70) return 'bg-red-900 text-red-300';
    if (score >= 40) return 'bg-orange-900 text-orange-300';
    return 'bg-green-900 text-green-300';
  };

  const filteredCases = cases.filter(c =>
    c.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    c.id.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const filteredEntities = entities.filter(e =>
    e.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <WorkspaceLayout>
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-500"></div>
        </div>
      </WorkspaceLayout>
    );
  }

  return (
    <WorkspaceLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-white">Dashboard Forensik Terintegrasi</h1>
            <p className="text-gray-400 mt-1">Data lengkap kasus, entitas, dan pengadaan</p>
          </div>
          <div className="flex items-center space-x-2">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-500" />
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Cari kasus atau entitas..."
                className="w-64 bg-gray-800 border border-gray-700 rounded-lg py-2 pl-10 pr-4 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500"
              />
            </div>
          </div>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <div className="flex items-center justify-between">
              <FileText className="w-5 h-5 text-cyan-400" />
              <span className="text-2xl font-bold text-white">{cases.length}</span>
            </div>
            <div className="text-xs text-gray-500 mt-1">Total Kasus</div>
          </div>
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <div className="flex items-center justify-between">
              <Building className="w-5 h-5 text-yellow-400" />
              <span className="text-2xl font-bold text-white">{entities.length}</span>
            </div>
            <div className="text-xs text-gray-500 mt-1">Total Entitas</div>
          </div>
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <div className="flex items-center justify-between">
              <ShoppingBag className="w-5 h-5 text-green-400" />
              <span className="text-2xl font-bold text-white">{procurementSummary?.totalVendors || 0}</span>
            </div>
            <div className="text-xs text-gray-500 mt-1">Total Vendor</div>
          </div>
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <div className="flex items-center justify-between">
              <DollarSign className="w-5 h-5 text-purple-400" />
              <span className="text-sm font-bold text-white">{formatCurrency(procurementSummary?.totalValue || 0)}</span>
            </div>
            <div className="text-xs text-gray-500 mt-1">Nilai Pengadaan</div>
          </div>
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <div className="flex items-center justify-between">
              <AlertTriangle className="w-5 h-5 text-red-400" />
              <span className="text-2xl font-bold text-white">{procurementSummary?.highRiskVendors || 0}</span>
            </div>
            <div className="text-xs text-gray-500 mt-1">Vendor Risiko Tinggi</div>
          </div>
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <div className="flex items-center justify-between">
              <Shield className="w-5 h-5 text-green-400" />
              <span className="text-2xl font-bold text-white">{procurementSummary?.integrityScore || 0}%</span>
            </div>
            <div className="text-xs text-gray-500 mt-1">Skor Integritas</div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex space-x-2 border-b border-gray-700">
          <button
            onClick={() => setSelectedTab('cases')}
            className={`px-4 py-2 text-sm font-medium rounded-t-lg transition flex items-center space-x-2 ${
              selectedTab === 'cases'
                ? 'bg-cyan-500/20 text-cyan-400 border-b-2 border-cyan-500'
                : 'text-gray-400 hover:text-gray-300'
            }`}
          >
            <FileText className="w-4 h-4" />
            <span>Kasus ({cases.length})</span>
          </button>
          <button
            onClick={() => setSelectedTab('entities')}
            className={`px-4 py-2 text-sm font-medium rounded-t-lg transition flex items-center space-x-2 ${
              selectedTab === 'entities'
                ? 'bg-cyan-500/20 text-cyan-400 border-b-2 border-cyan-500'
                : 'text-gray-400 hover:text-gray-300'
            }`}
          >
            <Building className="w-4 h-4" />
            <span>Entitas ({entities.length})</span>
          </button>
          <button
            onClick={() => setSelectedTab('procurement')}
            className={`px-4 py-2 text-sm font-medium rounded-t-lg transition flex items-center space-x-2 ${
              selectedTab === 'procurement'
                ? 'bg-cyan-500/20 text-cyan-400 border-b-2 border-cyan-500'
                : 'text-gray-400 hover:text-gray-300'
            }`}
          >
            <ShoppingBag className="w-4 h-4" />
            <span>Pengadaan</span>
          </button>
        </div>

        {/* Cases Tab */}
        {selectedTab === 'cases' && (
          <div className="space-y-3">
            {filteredCases.length === 0 ? (
              <div className="text-center py-12 text-gray-500">
                <FileText className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p>Tidak ada kasus ditemukan</p>
              </div>
            ) : (
              filteredCases.map((caseItem) => (
                <div key={caseItem.id} className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
                  <div 
                    className="p-4 cursor-pointer hover:bg-gray-700/30 transition flex justify-between items-center"
                    onClick={() => setExpandedCase(expandedCase === caseItem.id ? null : caseItem.id)}
                  >
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <FileText className="w-4 h-4 text-cyan-400" />
                        <h3 className="font-medium text-white">{caseItem.title}</h3>
                        <span className={`text-xs px-2 py-0.5 rounded ${getStatusBadge(caseItem.status)}`}>
                          {caseItem.status}
                        </span>
                        <span className={`text-xs px-2 py-0.5 rounded ${getPriorityBadge(caseItem.priority)}`}>
                          {caseItem.priority}
                        </span>
                      </div>
                      <div className="flex items-center space-x-4 text-xs text-gray-500">
                        <span>ID: {caseItem.id.substring(0, 8)}...</span>
                        <span>Dibuat: {new Date(caseItem.created_at).toLocaleDateString('id-ID')}</span>
                        {caseItem.assigned_to && <span>Ditugaskan ke: {caseItem.assigned_to}</span>}
                      </div>
                    </div>
                    {expandedCase === caseItem.id ? <ChevronUp className="w-5 h-5 text-gray-500" /> : <ChevronDown className="w-5 h-5 text-gray-500" />}
                  </div>
                  
                  {expandedCase === caseItem.id && (
                    <div className="px-4 pb-4 pt-2 border-t border-gray-700">
                      <p className="text-sm text-gray-400 mb-3">{caseItem.description || 'Tidak ada deskripsi'}</p>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                        {caseItem.procurement_value && (
                          <div>
                            <span className="text-gray-500">Nilai Pengadaan:</span>
                            <span className="ml-2 text-yellow-400">{formatCurrency(caseItem.procurement_value)}</span>
                          </div>
                        )}
                        {caseItem.vendor_count && (
                          <div>
                            <span className="text-gray-500">Jumlah Vendor:</span>
                            <span className="ml-2 text-white">{caseItem.vendor_count}</span>
                          </div>
                        )}
                        {caseItem.anomaly_score && (
                          <div>
                            <span className="text-gray-500">Skor Anomali:</span>
                            <div className="inline-flex items-center ml-2">
                              <div className="w-16 bg-gray-700 rounded-full h-1.5 mr-2">
                                <div className="bg-cyan-500 h-1.5 rounded-full" style={{ width: `${caseItem.anomaly_score}%` }} />
                              </div>
                              <span className="text-white">{caseItem.anomaly_score}%</span>
                            </div>
                          </div>
                        )}
                      </div>
                      <div className="mt-3 flex space-x-2">
                        <button className="text-xs px-3 py-1 bg-cyan-500/20 text-cyan-400 rounded hover:bg-cyan-500/30 transition">
                          <Eye className="w-3 h-3 inline mr-1" />
                          Lihat Detail
                        </button>
                        <button className="text-xs px-3 py-1 bg-gray-700 text-gray-300 rounded hover:bg-gray-600 transition">
                          <Download className="w-3 h-3 inline mr-1" />
                          Laporan
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        )}

        {/* Entities Tab */}
        {selectedTab === 'entities' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredEntities.length === 0 ? (
              <div className="col-span-full text-center py-12 text-gray-500">
                <Building className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p>Tidak ada entitas ditemukan</p>
              </div>
            ) : (
              filteredEntities.map((entity) => (
                <div 
                  key={entity.id} 
                  className={`bg-gray-800 rounded-lg border cursor-pointer transition hover:border-cyan-500/50 ${
                    selectedEntity?.id === entity.id ? 'border-cyan-500 bg-cyan-500/5' : 'border-gray-700'
                  }`}
                  onClick={() => setSelectedEntity(entity)}
                >
                  <div className="p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex items-center space-x-2">
                        <Building className="w-5 h-5 text-cyan-400" />
                        <h3 className="font-medium text-white">{entity.name}</h3>
                      </div>
                      <span className={`text-xs px-2 py-0.5 rounded ${getRiskBadge(entity.risk_score)}`}>
                        Risiko {entity.risk_score}%
                      </span>
                    </div>
                    <p className="text-xs text-gray-500 mt-1 capitalize">{entity.entity_type}</p>
                    <div className="mt-3">
                      <div className="flex justify-between text-xs mb-1">
                        <span className="text-gray-500">Keyakinan:</span>
                        <span className="text-gray-300">{entity.confidence}%</span>
                      </div>
                      <div className="w-full bg-gray-700 rounded-full h-1">
                        <div className="bg-cyan-500 h-1 rounded-full" style={{ width: `${entity.confidence}%` }} />
                      </div>
                    </div>
                    <div className="mt-2 text-xs text-gray-500">
                      Pertama terdeteksi: {new Date(entity.first_seen).toLocaleDateString('id-ID')}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {/* Procurement Tab */}
        {selectedTab === 'procurement' && procurementSummary && (
          <div className="space-y-6">
            {/* Procurement Stats Detail */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                <h3 className="text-sm font-medium text-gray-300 mb-4">Distribusi Risiko Vendor</h3>
                <div className="space-y-3">
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-400">Risiko Tinggi</span>
                      <span className="text-red-400">{procurementSummary.highRiskVendors} vendor</span>
                    </div>
                    <div className="w-full bg-gray-700 rounded-full h-2">
                      <div className="bg-red-500 h-2 rounded-full" style={{ width: `${(procurementSummary.highRiskVendors / Math.max(procurementSummary.totalVendors, 1)) * 100}%` }} />
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-400">Pola Kolusi</span>
                      <span className="text-yellow-400">{procurementSummary.collusionPatterns} pola</span>
                    </div>
                    <div className="w-full bg-gray-700 rounded-full h-2">
                      <div className="bg-yellow-500 h-2 rounded-full" style={{ width: `${Math.min(procurementSummary.collusionPatterns * 10, 100)}%` }} />
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
                <h3 className="text-sm font-medium text-gray-300 mb-4">Tren Nilai Pengadaan</h3>
                <div className="h-32 flex items-end space-x-2">
                  {[1.2, 0.9, 1.5, 1.8, 2.1, 2.5].map((value, idx) => (
                    <div key={idx} className="flex-1 flex flex-col items-center">
                      <div 
                        className="w-full bg-cyan-500 rounded-t"
                        style={{ height: `${(value / 3) * 100}%`, minHeight: '4px' }}
                      />
                      <span className="text-xs text-gray-500 mt-2">
                        {['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'][idx]}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Vendor List */}
            <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
              <div className="px-4 py-3 border-b border-gray-700">
                <h3 className="font-semibold text-white">Daftar Vendor</h3>
              </div>
              <div className="divide-y divide-gray-700">
                {[
                  { name: 'PT. Maju Jaya', risk: 92, contracts: 15, value: 2500000000 },
                  { name: 'CV. Karya Mandiri', risk: 88, contracts: 8, value: 1200000000 },
                  { name: 'PT. Bangun Nusantara', risk: 78, contracts: 12, value: 1800000000 },
                  { name: 'PT. Sejahtera Abadi', risk: 65, contracts: 5, value: 500000000 }
                ].map((vendor, idx) => (
                  <div key={idx} className="p-4 hover:bg-gray-700/30 transition">
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="font-medium text-white">{vendor.name}</h4>
                        <div className="text-xs text-gray-500 mt-1">
                          {vendor.contracts} kontrak • {formatCurrency(vendor.value)}
                        </div>
                      </div>
                      <div className="text-right">
                        <span className={`text-xs px-2 py-0.5 rounded ${getRiskBadge(vendor.risk)}`}>
                          Risiko {vendor.risk}%
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Entity Detail Modal */}
        {selectedEntity && (
          <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50" onClick={() => setSelectedEntity(null)}>
            <div className="bg-gray-800 rounded-lg border border-cyan-500/30 max-w-md w-full mx-4" onClick={(e) => e.stopPropagation()}>
              <div className="p-4 border-b border-gray-700 flex justify-between items-center">
                <h3 className="font-semibold text-white">Detail Entitas</h3>
                <button onClick={() => setSelectedEntity(null)} className="text-gray-400 hover:text-white">✕</button>
              </div>
              <div className="p-4">
                <div className="flex items-center space-x-2 mb-4">
                  <Building className="w-6 h-6 text-cyan-400" />
                  <h4 className="text-lg font-medium text-white">{selectedEntity.name}</h4>
                </div>
                <div className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-500">Tipe:</span>
                    <span className="text-white capitalize">{selectedEntity.entity_type}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Skor Risiko:</span>
                    <span className="text-yellow-400">{selectedEntity.risk_score}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Keyakinan:</span>
                    <span className="text-white">{selectedEntity.confidence}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Pertama Terdeteksi:</span>
                    <span className="text-white">{new Date(selectedEntity.first_seen).toLocaleDateString('id-ID')}</span>
                  </div>
                </div>
                <div className="mt-4 pt-3 border-t border-gray-700">
                  <button className="w-full px-3 py-2 bg-cyan-500/20 text-cyan-400 rounded hover:bg-cyan-500/30 transition text-sm">
                    Lihat Profil Risiko Lengkap
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </WorkspaceLayout>
  );
}
