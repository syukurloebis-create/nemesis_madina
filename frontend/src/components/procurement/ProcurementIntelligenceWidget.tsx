// src/components/procurement/ProcurementIntelligenceWidget.tsx
import React, { useEffect, useState } from 'react';
import { api } from '../../services/api';
import { ShoppingBag, TrendingUp, Award, AlertTriangle, DollarSign, Building2 } from 'lucide-react';
import { Link } from 'react-router-dom';

interface ProcurementStats {
  totalTenders: number;
  totalValue: number;
  avgBid: number;
  topVendors: { name: string; count: number; value: number }[];
  riskVendors: { name: string; riskScore: number }[];
}

const ProcurementIntelligenceWidget: React.FC = () => {
  const [stats, setStats] = useState<ProcurementStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProcurementStats();
  }, []);

  const loadProcurementStats = async () => {
    try {
      // Mock data - in production, call API
      const mockStats: ProcurementStats = {
        totalTenders: 5675,
        totalValue: 307046119600,
        avgBid: 54100000,
        topVendors: [
          { name: 'PT Teknologi Nusantara', count: 234, value: 7500000000 },
          { name: 'PT Cyber Security Indonesia', count: 156, value: 5200000000 },
          { name: 'CV Solusi Digital', count: 98, value: 3100000000 }
        ],
        riskVendors: [
          { name: 'CV Solusi Digital', riskScore: 85 },
          { name: 'PT Maju Jaya', riskScore: 72 },
          { name: 'PT Karya Mandiri', riskScore: 68 }
        ]
      };
      setStats(mockStats);
    } catch (error) {
      console.error('Error loading procurement stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-gray-200 rounded w-1/3"></div>
          <div className="grid grid-cols-2 gap-4">
            <div className="h-16 bg-gray-100 rounded"></div>
            <div className="h-16 bg-gray-100 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="px-4 py-3 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <ShoppingBag className="w-5 h-5 text-blue-600" />
            <h3 className="text-lg font-semibold text-gray-900">Procurement Intelligence</h3>
          </div>
          <Link to="/rup-data" className="text-sm text-blue-600 hover:text-blue-800">
            View Details →
          </Link>
        </div>
      </div>

      <div className="p-4">
        {/* Key Metrics */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="bg-blue-50 rounded-lg p-3">
            <div className="flex items-center gap-2">
              <ShoppingBag className="w-4 h-4 text-blue-500" />
              <span className="text-xs text-gray-500">Total Tenders</span>
            </div>
            <div className="text-xl font-bold text-gray-900">{stats?.totalTenders.toLocaleString()}</div>
          </div>
          <div className="bg-green-50 rounded-lg p-3">
            <div className="flex items-center gap-2">
              <DollarSign className="w-4 h-4 text-green-500" />
              <span className="text-xs text-gray-500">Total Value</span>
            </div>
            <div className="text-sm font-bold text-gray-900">{formatCurrency(stats?.totalValue || 0)}</div>
          </div>
        </div>

        {/* Top Vendors */}
        <div className="mb-4">
          <div className="flex items-center gap-2 mb-2">
            <Award className="w-4 h-4 text-yellow-500" />
            <h4 className="text-sm font-medium text-gray-700">Top Vendors by Contract</h4>
          </div>
          <div className="space-y-2">
            {stats?.topVendors.slice(0, 3).map((vendor, idx) => (
              <div key={idx} className="flex justify-between items-center text-sm">
                <span className="text-gray-600">{vendor.name}</span>
                <div className="flex items-center gap-3">
                  <span className="text-gray-500">{vendor.count} contracts</span>
                  <span className="font-medium text-gray-900">{formatCurrency(vendor.value)}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* High Risk Vendors */}
        <div>
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle className="w-4 h-4 text-red-500" />
            <h4 className="text-sm font-medium text-gray-700">High Risk Vendors</h4>
          </div>
          <div className="space-y-2">
            {stats?.riskVendors.map((vendor, idx) => (
              <div key={idx} className="flex justify-between items-center text-sm">
                <span className="text-gray-600">{vendor.name}</span>
                <div className="flex items-center gap-2">
                  <div className="w-16 h-1.5 bg-gray-200 rounded-full overflow-hidden">
                    <div 
                      className={`h-full rounded-full ${
                        vendor.riskScore >= 70 ? 'bg-red-500' : vendor.riskScore >= 50 ? 'bg-yellow-500' : 'bg-green-500'
                      }`}
                      style={{ width: `${vendor.riskScore}%` }}
                    ></div>
                  </div>
                  <span className="text-xs font-medium">{vendor.riskScore}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProcurementIntelligenceWidget;