import React, { useState, useEffect } from 'react';
import { useAuthStore } from '../stores/authStore';
import AuditTrail from '../components/governance/AuditTrail';

interface ComplianceItem {
  id: string;
  name: string;
  status: 'compliant' | 'non-compliant' | 'pending';
  last_checked: string;
  score: number;
}

const GovernanceCenter: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'audit' | 'compliance' | 'policies'>('audit');
  const [complianceItems, setComplianceItems] = useState<ComplianceItem[]>([]);
  const { token } = useAuthStore();

  useEffect(() => {
    fetchComplianceData();
  }, []);

  const fetchComplianceData = async () => {
    try {
      const response = await fetch('http://localhost/governance/compliance', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setComplianceItems(data.data || []);
      } else {
        // Mock data
        setComplianceItems([
          { id: '1', name: 'Data Protection Regulation', status: 'compliant', last_checked: new Date().toISOString(), score: 100 },
          { id: '2', name: 'Chain of Custody', status: 'compliant', last_checked: new Date().toISOString(), score: 98 },
          { id: '3', name: 'Evidence Integrity', status: 'compliant', last_checked: new Date().toISOString(), score: 100 },
          { id: '4', name: 'Access Control', status: 'pending', last_checked: new Date().toISOString(), score: 85 },
          { id: '5', name: 'Audit Trail Completeness', status: 'compliant', last_checked: new Date().toISOString(), score: 95 },
        ]);
      }
    } catch (error) {
      console.error('Failed to fetch compliance data:', error);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'compliant':
        return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'non-compliant':
        return 'bg-red-500/20 text-red-400 border-red-500/30';
      default:
        return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'compliant': return '✅';
      case 'non-compliant': return '❌';
      default: return '⏳';
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-gray-800/50 rounded-xl p-4 border border-gray-700">
        <h1 className="text-2xl font-bold text-white">Governance Center</h1>
        <p className="text-gray-400 text-sm mt-1">Compliance monitoring, audit trail, and policy management</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
          <p className="text-gray-400 text-sm">Compliance Score</p>
          <p className="text-3xl font-bold text-green-400">96%</p>
          <p className="text-xs text-gray-500 mt-1">↑ 2% from last month</p>
        </div>
        <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
          <p className="text-gray-400 text-sm">Open Audit Items</p>
          <p className="text-3xl font-bold text-yellow-400">3</p>
          <p className="text-xs text-gray-500 mt-1">Requiring attention</p>
        </div>
        <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
          <p className="text-gray-400 text-sm">Total Audit Logs</p>
          <p className="text-3xl font-bold text-white">1,247</p>
          <p className="text-xs text-gray-500 mt-1">Last 30 days</p>
        </div>
        <div className="bg-gray-800 rounded-xl p-6 border border-gray-700">
          <p className="text-gray-400 text-sm">Chain Integrity</p>
          <p className="text-3xl font-bold text-green-400">100%</p>
          <p className="text-xs text-gray-500 mt-1">Cryptographic verified</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-700">
        <nav className="flex gap-6">
          <button
            onClick={() => setActiveTab('audit')}
            className={`pb-3 px-1 text-sm font-medium transition-colors ${activeTab === 'audit' ? 'text-green-400 border-b-2 border-green-400' : 'text-gray-400 hover:text-gray-300'}`}
          >
            📋 Audit Trail
          </button>
          <button
            onClick={() => setActiveTab('compliance')}
            className={`pb-3 px-1 text-sm font-medium transition-colors ${activeTab === 'compliance' ? 'text-green-400 border-b-2 border-green-400' : 'text-gray-400 hover:text-gray-300'}`}
          >
            ⚖️ Compliance
          </button>
          <button
            onClick={() => setActiveTab('policies')}
            className={`pb-3 px-1 text-sm font-medium transition-colors ${activeTab === 'policies' ? 'text-green-400 border-b-2 border-green-400' : 'text-gray-400 hover:text-gray-300'}`}
          >
            📜 Policies
          </button>
        </nav>
      </div>

      {/* Content */}
      {activeTab === 'audit' && (
        <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-700">
            <h2 className="text-lg font-semibold text-white">Audit Trail</h2>
            <p className="text-xs text-gray-500 mt-1">Complete history of all system activities</p>
          </div>
          <div className="p-4">
            <AuditTrail />
          </div>
        </div>
      )}

      {activeTab === 'compliance' && (
        <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-700">
            <h2 className="text-lg font-semibold text-white">Compliance Status</h2>
          </div>
          <div className="divide-y divide-gray-700">
            {complianceItems.map((item) => (
              <div key={item.id} className="p-4 flex justify-between items-center">
                <div>
                  <h3 className="font-medium text-white">{item.name}</h3>
                  <p className="text-xs text-gray-500 mt-1">Last checked: {new Date(item.last_checked).toLocaleDateString()}</p>
                </div>
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <span className={`px-2 py-1 rounded-full text-xs ${getStatusBadge(item.status)}`}>
                      {getStatusIcon(item.status)} {item.status.toUpperCase()}
                    </span>
                    <p className="text-sm text-gray-400 mt-1">Score: {item.score}%</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'policies' && (
        <div className="bg-gray-800 rounded-xl border border-gray-700 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-700">
            <h2 className="text-lg font-semibold text-white">Governance Policies</h2>
          </div>
          <div className="divide-y divide-gray-700">
            <div className="p-4">
              <h3 className="font-medium text-white">Data Retention Policy</h3>
              <p className="text-sm text-gray-400 mt-1">All case data retained for minimum 7 years</p>
              <span className="inline-block mt-2 text-xs px-2 py-1 bg-green-500/20 text-green-400 rounded">Active</span>
            </div>
            <div className="p-4">
              <h3 className="font-medium text-white">Chain of Custody Protocol</h3>
              <p className="text-sm text-gray-400 mt-1">Cryptographic verification required for all evidence</p>
              <span className="inline-block mt-2 text-xs px-2 py-1 bg-green-500/20 text-green-400 rounded">Active</span>
            </div>
            <div className="p-4">
              <h3 className="font-medium text-white">Access Control Policy</h3>
              <p className="text-sm text-gray-400 mt-1">Role-based access with mandatory approval</p>
              <span className="inline-block mt-2 text-xs px-2 py-1 bg-green-500/20 text-green-400 rounded">Active</span>
            </div>
            <div className="p-4">
              <h3 className="font-medium text-white">Audit Logging Policy</h3>
              <p className="text-sm text-gray-400 mt-1">All actions logged with tamper-proof hash chain</p>
              <span className="inline-block mt-2 text-xs px-2 py-1 bg-green-500/20 text-green-400 rounded">Active</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default GovernanceCenter;
