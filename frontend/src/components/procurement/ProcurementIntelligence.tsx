import React, { useState, useEffect } from 'react';
import { 
  Package, 
  Users, 
  TrendingUp, 
  AlertTriangle,
  FileText,
  Building,
  DollarSign,
  Calendar,
  ChevronRight,
  Download,
  Filter,
  Search,
  RefreshCw
} from 'lucide-react';
import { procurementApi, vendorApi } from '../../services/api';

interface ProcurementPackage {
  id: string;
  title: string;
  vendor: string;
  value: number;
  status: string;
  riskScore: number;
  riskLevel: string;
  createdAt: Date;
  suspiciousIndicators: string[];
  relatedEntities: string[];
}

interface Vendor {
  id: string;
  name: string;
  type: string;
  riskScore: number;
  totalPackages: number;
  totalValue: number;
  suspiciousCount: number;
  status: string;
  lastActivity: Date;
}

export const ProcurementIntelligence: React.FC = () => {
  const [packages, setPackages] = useState<ProcurementPackage[]>([]);
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [rupData, vendorData] = await Promise.all([
        procurementApi.getRUPStats().catch(() => ({ data: {} })),
        vendorApi.getSuspicious().catch(() => ({ data: [] })),
      ]);

      // Transform procurement data
      const transformedPackages = transformPackages(rupData.data);
      const transformedVendors = transformVendors(vendorData.data);

      setPackages(transformedPackages);
      setVendors(transformedVendors);
    } catch (err) {
      setError('Failed to load procurement data');
      console.error('Error loading procurement data:', err);
    } finally {
      setLoading(false);
    }
  };

  const transformPackages = (data: any): ProcurementPackage[] => {
    if (!data) return [];
    // If data is array, use it directly
    if (Array.isArray(data)) {
      return data.map((item: any, index:number) => ({
        id: item.id || item.package_id || `PKG-${Date.now()}-${index}`,
        title: item.title || item.name || 'Untitled Package',
        vendor: item.vendor || item.vendor_name || 'Unknown Vendor',
        value: item.value || item.total_value || 0,
        status: item.status || 'PUBLISHED',
        riskScore: item.risk_score || item.riskScore || 0,
        riskLevel: determineRiskLevel(item.risk_score || item.riskScore || 0),
        createdAt: new Date(item.created_at || item.createdAt || Date.now()),
        suspiciousIndicators: item.indicators || item.suspicious_indicators || [],
        relatedEntities: item.related_entities || item.entities || [],
      }));
    }
    return [];
  };

  const transformVendors = (data: any): Vendor[] => {
    if (!data) return [];

    if (Array.isArray(data)) {
      return data.map((item: any, index: number) => ({
        id: item.id || item.vendor_id || `VEN-${crypto.randomUUID()}`,
        name: item.name || item.vendor_name || 'Unknown Vendor',
        type: item.type || item.vendor_type || 'Unknown',
        riskScore: item.risk_score || item.riskScore || 0,
        totalPackages: item.total_packages || item.totalPackages || 0,
        totalValue: item.total_value || item.totalValue || 0,
        suspiciousCount: item.suspicious_count || item.suspiciousCount || 0,
        status: item.status || 'ACTIVE',
        lastActivity: new Date(
          item.last_activity || item.lastActivity || Date.now()
        ),
      }));
    }

    return [];
  };

  const determineRiskLevel = (score: number): string => {
    if (score >= 80) return 'CRITICAL';
    if (score >= 60) return 'HIGH';
    if (score >= 40) return 'MEDIUM';
    return 'LOW';
  };

  const getRiskBadge = (level: string) => {
    switch (level) {
      case 'CRITICAL':
        return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'HIGH':
        return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
      case 'MEDIUM':
        return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      default:
        return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
    }
  };

  const getStatusBadge = (status: string) => {
    const statusMap: Record<string, string> = {
      'SUSPICIOUS': 'bg-red-500/20 text-red-400 border-red-500/30',
      'UNDER_INVESTIGATION': 'bg-orange-500/20 text-orange-400 border-orange-500/30',
      'BLACKLISTED': 'bg-red-500/20 text-red-400 border-red-500/30',
      'SUSPENDED': 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
      'ACTIVE': 'bg-green-500/20 text-green-400 border-green-500/30',
    };
    return statusMap[status] || 'bg-gray-500/20 text-gray-400 border-gray-500/30';
  };

  const formatCurrency = (amount: number) => {
    if (amount === 0) return 'Rp 0';
    return new Intl.NumberFormat('id-ID', {
      style: 'currency',
      currency: 'IDR',
      minimumFractionDigits: 0,
    }).format(amount);
  };

  const filteredPackages = packages.filter(p => 
    p.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    p.vendor.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="grid grid-cols-4 gap-4">
          {[1, 2, 3, 4].map(i => (
            <div key={i} className="bg-dark-card p-4 rounded-lg h-24"></div>
          ))}
        </div>
        <div className="bg-dark-card p-6 rounded-lg h-64"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-dark-card border border-red-500/30 rounded-lg p-8 text-center">
        <AlertTriangle className="w-12 h-12 text-red-400 mx-auto mb-4" />
        <p className="text-red-400">{error}</p>
        <button 
          onClick={loadData}
          className="mt-4 px-4 py-2 bg-primary-500 text-white rounded hover:bg-primary-600"
        >
          <RefreshCw className="w-4 h-4 inline mr-2" />
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">📦 Procurement Intelligence</h2>
          <p className="text-dark-muted">Monitor vendor risk and suspicious procurement patterns</p>
        </div>
        <button 
          onClick={loadData}
          className="flex items-center gap-2 px-4 py-2 bg-primary-500/10 text-primary-400 border border-primary-500/20 rounded-lg hover:bg-primary-500/20 transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          Refresh
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Total Packages"
          value={packages.length}
          icon={Package}
          color="text-blue-400"
        />
        <StatCard
          label="Total Value"
          value={formatCurrency(packages.reduce((sum, p) => sum + p.value, 0))}
          icon={DollarSign}
          color="text-green-400"
        />
        <StatCard
          label="High Risk Vendors"
          value={vendors.filter(v => v.riskScore > 60).length}
          icon={AlertTriangle}
          color="text-orange-400"
        />
        <StatCard
          label="Suspicious Packages"
          value={packages.filter(p => p.riskLevel === 'HIGH' || p.riskLevel === 'CRITICAL').length}
          icon={Building}
          color="text-red-400"
        />
      </div>

      {/* Vendor List */}
      <div className="bg-dark-card border border-dark-border rounded-lg overflow-hidden">
        <div className="p-4 border-b border-dark-border flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Users className="w-5 h-5 text-dark-muted" />
            <h3 className="font-semibold text-white">Vendor Risk Overview</h3>
            <span className="text-sm text-dark-muted">{vendors.length} vendors</span>
          </div>
          <div className="flex items-center gap-2">
            <button className="p-2 rounded hover:bg-dark-hover text-dark-muted hover:text-white transition-colors">
              <Filter className="w-4 h-4" />
            </button>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-dark-muted" />
              <input
                type="text"
                placeholder="Search vendors..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white placeholder-dark-muted focus:outline-none focus:border-primary-500"
              />
            </div>
          </div>
        </div>

        {vendors.length === 0 ? (
          <div className="p-8 text-center text-dark-muted">
            <Building className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>No vendor data available</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-dark-bg/50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-dark-muted uppercase">Vendor</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-dark-muted uppercase">Type</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-dark-muted uppercase">Status</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-dark-muted uppercase">Risk Score</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-dark-muted uppercase">Packages</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-dark-muted uppercase">Total Value</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-dark-muted uppercase">Suspicious</th>
                  <th className="px-4 py-3 text-center text-xs font-medium text-dark-muted uppercase">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-dark-border">
                {vendors.slice(0, 10).map((vendor) => (
                  <tr key={vendor.id} className="hover:bg-dark-hover/50 transition-colors">
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-3">
                        <Building className="w-4 h-4 text-dark-muted" />
                        <span className="text-white font-medium">{vendor.name}</span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-dark-muted">{vendor.type}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 rounded text-xs font-medium border ${getStatusBadge(vendor.status)}`}>
                        {vendor.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right">
                      <span className={`px-2 py-1 rounded text-xs font-medium border ${getRiskBadge(determineRiskLevel(vendor.riskScore))}`}>
                        {vendor.riskScore}%
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right text-white">{vendor.totalPackages}</td>
                    <td className="px-4 py-3 text-right text-white">{formatCurrency(vendor.totalValue)}</td>
                    <td className="px-4 py-3 text-right">
                      {vendor.suspiciousCount > 0 ? (
                        <span className="px-2 py-1 rounded text-xs font-medium bg-red-500/20 text-red-400">
                          {vendor.suspiciousCount} indicators
                        </span>
                      ) : (
                        <span className="text-dark-muted text-sm">-</span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-center">
                      <button className="p-1 rounded hover:bg-dark-hover text-dark-muted hover:text-white transition-colors">
                        <ChevronRight className="w-5 h-5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Suspicious Packages Detail */}
      {filteredPackages.filter(p => p.riskLevel === 'HIGH' || p.riskLevel === 'CRITICAL').length > 0 && (
        <div className="bg-dark-card border border-dark-border rounded-lg p-4">
          <h3 className="font-semibold text-white mb-4 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-red-400" />
            Suspicious Packages
          </h3>
          <div className="space-y-4">
            {filteredPackages
              .filter(p => p.riskLevel === 'HIGH' || p.riskLevel === 'CRITICAL')
              .slice(0, 5)
              .map((pkg) => (
                <div key={pkg.id} className="border border-dark-border rounded-lg p-4 hover:border-red-500/30 transition-colors">
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="flex items-center gap-3 mb-1">
                        <span className={`px-2 py-0.5 rounded text-xs font-medium border ${getRiskBadge(pkg.riskLevel)}`}>
                          {pkg.riskLevel}
                        </span>
                        <span className="text-dark-muted text-sm">{pkg.id}</span>
                        <span className="text-dark-muted text-sm flex items-center gap-1">
                          <Calendar className="w-3 h-3" />
                          {new Date(pkg.createdAt).toLocaleDateString()}
                        </span>
                      </div>
                      <h4 className="text-white font-medium">{pkg.title}</h4>
                      <p className="text-dark-muted text-sm">Vendor: {pkg.vendor}</p>
                      <div className="flex items-center gap-4 mt-2 text-sm">
                        <span className="text-dark-muted">Value: <span className="text-white">{formatCurrency(pkg.value)}</span></span>
                        <span className="text-dark-muted">Risk: <span className="text-orange-400">{pkg.riskScore}%</span></span>
                      </div>
                      {pkg.suspiciousIndicators.length > 0 && (
                        <div className="flex flex-wrap gap-2 mt-2">
                          {pkg.suspiciousIndicators.map((indicator, idx) => (
                            <span key={idx} className="px-2 py-0.5 text-xs bg-red-500/10 text-red-400 rounded-full border border-red-500/20">
                              {indicator}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                    <button className="flex items-center gap-2 px-3 py-1.5 bg-primary-500/10 text-primary-400 border border-primary-500/20 rounded hover:bg-primary-500/20 transition-colors text-sm">
                      Investigate
                    </button>
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  );
};

// Stat Card Component
const StatCard: React.FC<{
  label: string;
  value: string | number;
  icon: React.FC<{ className?: string }>;
  color?: string;
}> = ({ label, value, icon: Icon, color = 'text-white' }) => (
  <div className="bg-dark-card border border-dark-border rounded-lg p-4">
    <div className="flex items-center gap-2 text-dark-muted text-sm">
      <Icon className={`w-4 h-4 ${color}`} />
      <span>{label}</span>
    </div>
    <div className={`text-xl font-bold ${color}`}>{value}</div>
  </div>
);

export default ProcurementIntelligence;
