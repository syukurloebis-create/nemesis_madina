import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

interface Vendor {
  id: string;
  name: string;
  registration_number: string;
  tax_id: string;
  address: string;
  city: string;
  province: string;
  postal_code: string;
  phone: string;
  email: string;
  website: string;
  established_year: number;
  business_type: string;
  classification: string;
  risk_score: number;
  risk_level: string;
  status: string;
  related_cases: number;
  total_contracts: number;
  total_value: number;
  last_audit: string;
  created_at: string;
  updated_at: string;
  metadata: Record<string, any>;
}

interface VendorCollusion {
  id: string;
  vendor_ids: string[];
  pattern_type: string;
  confidence: number;
  severity: string;
  description: string;
  detected_at: string;
}

const VendorList: React.FC = () => {
  const navigate = useNavigate();
  const [vendors] = useState<Vendor[]>([
    {
      id: '1', name: 'PT. Maju Jaya', registration_number: '1234567890', tax_id: '01.234.567.8-901.000',
      address: 'Jl. Sudirman No. 123', city: 'Jakarta Selatan', province: 'DKI Jakarta', postal_code: '12190',
      phone: '021-1234567', email: 'info@majujaya.co.id', website: 'www.majujaya.co.id',
      established_year: 2010, business_type: 'Kontraktor', classification: 'large',
      risk_score: 92, risk_level: 'critical', status: 'active', related_cases: 5,
      total_contracts: 12, total_value: 450, last_audit: '2026-05-15',
      created_at: new Date().toISOString(), updated_at: new Date().toISOString(), metadata: {}
    },
    {
      id: '2', name: 'CV. Karya Mandiri', registration_number: '9876543210', tax_id: '02.345.678.9-012.000',
      address: 'Jl. Gatot Subroto No. 45', city: 'Jakarta Pusat', province: 'DKI Jakarta', postal_code: '10270',
      phone: '021-7654321', email: 'cs@karyamandiri.com', website: 'www.karyamandiri.com',
      established_year: 2015, business_type: 'Penyedia Jasa', classification: 'medium',
      risk_score: 88, risk_level: 'high', status: 'active', related_cases: 3,
      total_contracts: 8, total_value: 280, last_audit: '2026-04-20',
      created_at: new Date().toISOString(), updated_at: new Date().toISOString(), metadata: {}
    },
    {
      id: '3', name: 'PT. Bangun Nusantara', registration_number: '5555555555', tax_id: '03.456.789.0-123.000',
      address: 'Jl. Thamrin No. 78', city: 'Jakarta Pusat', province: 'DKI Jakarta', postal_code: '10350',
      phone: '021-5551234', email: 'info@bangunnusantara.com', website: 'www.bangunnusantara.com',
      established_year: 2008, business_type: 'Konstruksi', classification: 'large',
      risk_score: 78, risk_level: 'medium', status: 'active', related_cases: 2,
      total_contracts: 15, total_value: 620, last_audit: '2026-03-10',
      created_at: new Date().toISOString(), updated_at: new Date().toISOString(), metadata: {}
    },
  ]);

  const [collusions] = useState<VendorCollusion[]>([
    { id: '1', vendor_ids: ['1', '2'], pattern_type: 'address', confidence: 92, severity: 'high', description: 'Multiple vendors sharing same registered address pattern', detected_at: new Date().toISOString() },
    { id: '2', vendor_ids: ['1', '3'], pattern_type: 'bid_rigging', confidence: 88, severity: 'critical', description: 'Suspicious pattern of rotating lowest bidders', detected_at: new Date().toISOString() },
  ]);

  const [searchTerm, setSearchTerm] = useState('');
  const [riskFilter, setRiskFilter] = useState<string>('all');
  const [selectedVendor, setSelectedVendor] = useState<Vendor | null>(null);

  const handleViewRelatedCases = (vendor: Vendor) => {
    navigate(`/investigation?vendor=${encodeURIComponent(vendor.name)}&vendor_id=${vendor.id}`);
  };

  const handleExportReport = (vendor: Vendor) => {
    const reportData = {
      vendor_name: vendor.name,
      registration_number: vendor.registration_number,
      tax_id: vendor.tax_id,
      address: vendor.address,
      business_type: vendor.business_type,
      classification: vendor.classification,
      risk_score: vendor.risk_score,
      risk_level: vendor.risk_level,
      status: vendor.status,
      total_contracts: vendor.total_contracts,
      total_value: vendor.total_value,
      related_cases: vendor.related_cases,
      generated_at: new Date().toISOString(),
      report_type: 'vendor_risk_assessment'
    };
    
    const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `vendor_${vendor.name.replace(/\s/g, '_')}_report.json`;
    a.click();
    URL.revokeObjectURL(url);
    
    alert(`✅ Report for ${vendor.name} exported successfully!`);
  };

  const getRiskColor = (score: number) => {
    if (score >= 85) return 'text-red-500';
    if (score >= 70) return 'text-orange-500';
    if (score >= 40) return 'text-yellow-500';
    return 'text-green-500';
  };

  const getRiskBgColor = (score: number) => {
    if (score >= 85) return 'bg-red-500/20';
    if (score >= 70) return 'bg-orange-500/20';
    if (score >= 40) return 'bg-yellow-500/20';
    return 'bg-green-500/20';
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-500/20 text-green-400';
      case 'suspended': return 'bg-yellow-500/20 text-yellow-400';
      case 'blacklisted': return 'bg-red-500/20 text-red-400';
      default: return 'bg-gray-500/20 text-gray-400';
    }
  };

  const filteredVendors = vendors.filter(vendor => {
    const matchesSearch = vendor.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          vendor.registration_number.includes(searchTerm);
    const matchesRisk = riskFilter === 'all' || vendor.risk_level === riskFilter;
    return matchesSearch && matchesRisk;
  });

  const getVendorCollusions = (vendorId: string) => {
    return collusions.filter(c => c.vendor_ids.includes(vendorId));
  };

  const formatValue = (value: number) => {
    return value?.toLocaleString() || '0';
  };

  return (
    <div className="space-y-6">
      <div className="bg-gray-800/50 rounded-xl p-4 border border-gray-700">
        <h1 className="text-2xl font-bold text-white">Vendor Directory</h1>
        <p className="text-gray-400 text-sm mt-1">Manage vendors, track risk profiles, and detect collusion patterns</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gray-800 rounded-xl p-4 border border-gray-700">
          <p className="text-gray-400 text-sm">Total Vendors</p>
          <p className="text-2xl font-bold text-white">{vendors.length}</p>
        </div>
        <div className="bg-gray-800 rounded-xl p-4 border border-gray-700">
          <p className="text-gray-400 text-sm">High Risk Vendors</p>
          <p className="text-2xl font-bold text-red-500">{vendors.filter(v => v.risk_level === 'critical' || v.risk_level === 'high').length}</p>
        </div>
        <div className="bg-gray-800 rounded-xl p-4 border border-gray-700">
          <p className="text-gray-400 text-sm">Active Contracts</p>
          <p className="text-2xl font-bold text-white">{vendors.reduce((sum, v) => sum + (v.total_contracts || 0), 0)}</p>
        </div>
        <div className="bg-gray-800 rounded-xl p-4 border border-gray-700">
          <p className="text-gray-400 text-sm">Total Contract Value</p>
          <p className="text-2xl font-bold text-green-400">
            Rp {formatValue(vendors.reduce((sum, v) => sum + (v.total_value || 0), 0))}M
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-gray-800 rounded-xl p-4 border border-gray-700">
        <div className="flex flex-wrap gap-4">
          <div className="flex-1">
            <input
              type="text"
              placeholder="Search by name or registration number..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400"
            />
          </div>
          <select
            value={riskFilter}
            onChange={(e) => setRiskFilter(e.target.value)}
            className="px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
          >
            <option value="all">All Risk Levels</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>
      </div>

      {/* Vendor Table */}
      <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-900">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">Vendor</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">Registration</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">Risk Score</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">Contracts</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">Value (M)</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">Collusions</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-700">
              {filteredVendors.map((vendor) => {
                const vendorCollusions = getVendorCollusions(vendor.id);
                return (
                  <tr key={vendor.id} className="hover:bg-gray-700/30">
                    <td className="px-6 py-4">
                      <div>
                        <p className="font-medium text-white">{vendor.name}</p>
                        <p className="text-xs text-gray-500">{vendor.business_type}</p>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-gray-300">{vendor.registration_number}</td>
                    <td className="px-6 py-4">
                      <div className={`inline-flex items-center px-2 py-1 rounded-full text-sm font-semibold ${getRiskBgColor(vendor.risk_score)} ${getRiskColor(vendor.risk_score)}`}>
                        {vendor.risk_score}%
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-1 rounded-full text-xs ${getStatusBadge(vendor.status)}`}>
                        {vendor.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-white">{vendor.total_contracts}</td>
                    <td className="px-6 py-4 text-white">{formatValue(vendor.total_value)}</td>
                    <td className="px-6 py-4">
                      {vendorCollusions.length > 0 ? (
                        <span className="text-red-400 font-semibold">{vendorCollusions.length}</span>
                      ) : (
                        <span className="text-gray-500">-</span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <button
                        onClick={() => setSelectedVendor(vendor)}
                        className="px-3 py-1 text-xs bg-blue-500/20 text-blue-400 rounded-lg hover:bg-blue-500/30"
                      >
                        View Details
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Vendor Detail Modal */}
      {selectedVendor && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
          <div className="bg-gray-800 rounded-xl max-w-3xl w-full max-h-[85vh] overflow-y-auto">
            <div className="sticky top-0 bg-gray-800 px-6 py-4 border-b border-gray-700 flex justify-between items-center">
              <h2 className="text-xl font-bold text-white">Vendor Details</h2>
              <button onClick={() => setSelectedVendor(null)} className="text-gray-400 hover:text-white">✕</button>
            </div>
            
            <div className="p-6 space-y-6">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="text-2xl font-bold text-white">{selectedVendor.name}</h3>
                  <p className="text-gray-400">{selectedVendor.business_type} • {selectedVendor.classification}</p>
                </div>
                <div className={`px-4 py-2 rounded-full ${getRiskBgColor(selectedVendor.risk_score)}`}>
                  <span className={`text-xl font-bold ${getRiskColor(selectedVendor.risk_score)}`}>
                    {selectedVendor.risk_score}% Risk
                  </span>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-700/30 rounded-lg p-3">
                  <p className="text-gray-400 text-sm">Registration</p>
                  <p className="text-white">{selectedVendor.registration_number}</p>
                </div>
                <div className="bg-gray-700/30 rounded-lg p-3">
                  <p className="text-gray-400 text-sm">Tax ID</p>
                  <p className="text-white">{selectedVendor.tax_id}</p>
                </div>
                <div className="bg-gray-700/30 rounded-lg p-3">
                  <p className="text-gray-400 text-sm">Email</p>
                  <p className="text-white">{selectedVendor.email}</p>
                </div>
                <div className="bg-gray-700/30 rounded-lg p-3">
                  <p className="text-gray-400 text-sm">Phone</p>
                  <p className="text-white">{selectedVendor.phone}</p>
                </div>
              </div>

              <div className="bg-gray-700/30 rounded-lg p-3">
                <p className="text-gray-400 text-sm">Address</p>
                <p className="text-white">{selectedVendor.address}, {selectedVendor.city}, {selectedVendor.province}</p>
              </div>

              {getVendorCollusions(selectedVendor.id).length > 0 && (
                <div>
                  <h4 className="font-semibold text-white mb-3">Collusion Patterns</h4>
                  <div className="space-y-2">
                    {getVendorCollusions(selectedVendor.id).map((collusion) => (
                      <div key={collusion.id} className="bg-red-500/10 border border-red-500/30 rounded-lg p-3">
                        <div className="flex justify-between">
                          <span className="font-medium text-red-400">{collusion.pattern_type.replace(/_/g, ' ').toUpperCase()}</span>
                          <span className="text-sm text-white">Confidence: {collusion.confidence}%</span>
                        </div>
                        <p className="text-sm text-gray-400 mt-1">{collusion.description}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="flex gap-3 pt-4 border-t border-gray-700">
                <button
                  onClick={() => {
                    setSelectedVendor(null);
                    handleViewRelatedCases(selectedVendor);
                  }}
                  className="flex-1 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                >
                  📋 View Related Cases
                </button>
                <button
                  onClick={() => handleExportReport(selectedVendor)}
                  className="flex-1 px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition-colors"
                >
                  📊 Export Report
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default VendorList;
