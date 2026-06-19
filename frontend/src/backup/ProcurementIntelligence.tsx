import React, { useState, useEffect } from 'react';
import { WorkspaceLayout } from '../WorkspaceLayout';
import { procurementApi } from '../services/procurementApi';
import type { ProcurementSummary, CollusionPattern } from '../services/procurementApi';
import { ShoppingBag, Building, DollarSign, AlertTriangle, Shield, TrendingUp } from 'lucide-react';

export default function ProcurementIntelligence() {
  const [summary, setSummary] = useState<ProcurementSummary | null>(null);
  const [collusionPatterns, setCollusionPatterns] = useState<CollusionPattern[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedTab, setSelectedTab] = useState<'overview' | 'collusion'>('overview');

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
      case 'critical': return 'bg-red-900 text-red-300';
      case 'high': return 'bg-orange-900 text-orange-300';
      case 'medium': return 'bg-yellow-900 text-yellow-300';
      default: return 'bg-gray-700 text-gray-300';
    }
  };

  if (loading) {
    return (
      <WorkspaceLayout>
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyan-500"></div>
        </div>
      </WorkspaceLayout>
    );
  }

  return (
    <WorkspaceLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-white">Intelijen Pengadaan</h1>
          <p className="text-gray-400 mt-1">Deteksi anomali, kolusi, dan risiko dalam proses pengadaan</p>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
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
              <span className="text-sm font-bold text-white">{formatCurrency(summary?.totalValue || 0)}</span>
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
              <Shield className="w-5 h-5 text-green-400" />
              <span className="text-2xl font-bold text-white">{summary?.integrityScore || 0}%</span>
            </div>
            <div className="text-xs text-gray-500 mt-1">Skor Integritas</div>
          </div>
        </div>

        <div className="flex space-x-2 border-b border-gray-700">
          <button
            onClick={() => setSelectedTab('overview')}
            className={`px-4 py-2 text-sm font-medium rounded-t-lg transition ${
              selectedTab === 'overview'
                ? 'bg-cyan-500/20 text-cyan-400 border-b-2 border-cyan-500'
                : 'text-gray-400 hover:text-gray-300'
            }`}
          >
            📊 Ikhtisar
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
        </div>

        {selectedTab === 'overview' && (
          <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
            <h3 className="text-sm font-medium text-gray-300 mb-4">Tren Nilai Pengadaan</h3>
            <div className="h-32 flex items-end space-x-2">
              {(summary?.monthlyTrend || []).map((item, idx) => (
                <div key={idx} className="flex-1 flex flex-col items-center">
                  <div 
                    className="w-full bg-cyan-500 rounded-t"
                    style={{ height: `${(item.value / 3000000000) * 100}%`, minHeight: '4px' }}
                  />
                  <span className="text-xs text-gray-500 mt-2">{item.month}</span>
                </div>
              ))}
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
                        {pattern.severity.toUpperCase()}
                      </span>
                      <h4 className="font-medium text-white">{pattern.type}</h4>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className="text-xs text-gray-500">Keyakinan:</span>
                      <div className="w-24 bg-gray-700 rounded-full h-1.5">
                        <div className="bg-cyan-500 h-1.5 rounded-full" style={{ width: `${pattern.confidence}%` }} />
                      </div>
                      <span className="text-xs text-cyan-400">{pattern.confidence}%</span>
                    </div>
                  </div>
                  <p className="text-sm text-gray-400 mt-2">{pattern.description}</p>
                  <div className="mt-3 flex flex-wrap gap-2">
                    {pattern.entities.map((entity, idx) => (
                      <span key={idx} className="text-xs bg-gray-700 px-2 py-1 rounded">🏢 {entity}</span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </WorkspaceLayout>
  );
}
