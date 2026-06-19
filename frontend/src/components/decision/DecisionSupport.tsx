// DecisionSupport.tsx - Clean Version
import React, { useState, useEffect } from 'react';
import {
  CheckCircle,
  AlertTriangle,
  Clock,
  FileText,
  Eye,
  RefreshCw,
  Loader2,
  XCircle
} from 'lucide-react';

interface Decision {
  id: string;
  title: string;
  description: string;
  priority: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  status: string;
  due_date: string;
  case_title: string;
  justification: any[];
}

interface DecisionSupportProps {
  caseId?: string;
  className?: string;
}

export const DecisionSupport: React.FC<DecisionSupportProps> = ({ 
  caseId,
  className = '' 
}) => {
  const [decisions, setDecisions] = useState<Decision[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedDecision, setSelectedDecision] = useState<Decision | null>(null);
  const [showReview, setShowReview] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);

  const fetchDecisions = () => {
    setLoading(true);
    setTimeout(() => {
      setDecisions([
        {
          id: 'b6b4997a',
          title: 'Audit Investigatif PT. Dexa Medica',
          description: 'Lakukan audit mendalam terhadap hubungan kepemilikan dan transaksi',
          priority: 'CRITICAL',
          status: 'PENDING',
          due_date: '2026-06-25',
          case_title: 'Audit RUP Vendor Test',
          justification: [
            { factor: 'Priority Level', contribution: 52.2, description: 'Kasus memiliki prioritas HIGH' },
            { factor: 'Collusion Network', contribution: 30.7, description: 'Terlibat dalam jaringan kolusi' },
            { factor: 'Insufficient Evidence', contribution: 17.1, description: 'Bukti belum lengkap' }
          ]
        },
        {
          id: 'b8ab698c',
          title: 'Permintaan Klarifikasi CV. Anugrah',
          description: 'Minta klarifikasi terkait perbedaan harga yang signifikan',
          priority: 'HIGH',
          status: 'PENDING',
          due_date: '2026-07-02',
          case_title: 'Audit RUP Vendor Test',
          justification: []
        }
      ]);
      setLoading(false);
    }, 300);
  };

  useEffect(() => {
    fetchDecisions();
  }, [caseId]);

  const handleRefresh = () => {
    fetchDecisions();
  };

  const handleReview = (decision: Decision) => {
    setSelectedDecision(decision);
    setShowReview(true);
  };

  const handleAction = (action: string) => {
    setActionLoading(true);
    setTimeout(() => {
      const messages: Record<string, string> = {
        approve: '✅ Rekomendasi disetujui!',
        reject: '❌ Rekomendasi ditolak!',
        request_changes: '🔄 Permintaan revisi dikirim!'
      };
      alert(messages[action] || 'Action successful!');
      setShowReview(false);
      setActionLoading(false);
      fetchDecisions();
    }, 500);
  };

  const getPriorityBadge = (priority: string) => {
    const colors: Record<string, string> = {
      CRITICAL: 'bg-red-500/20 text-red-400 border-red-500/30',
      HIGH: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
      MEDIUM: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
      LOW: 'bg-green-500/20 text-green-400 border-green-500/30'
    };
    return colors[priority] || colors.LOW;
  };

  if (loading) {
    return (
      <div className={`glass-card p-4 ${className}`}>
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-gray-700 rounded w-1/3" />
          <div className="grid grid-cols-4 gap-2">
            {[1, 2, 3, 4].map(i => <div key={i} className="h-16 bg-gray-700 rounded" />)}
          </div>
          <div className="space-y-2">
            {[1, 2].map(i => <div key={i} className="h-20 bg-gray-700 rounded" />)}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`glass-card p-4 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <span className="text-lg">⚖️</span>
          <h3 className="text-sm font-semibold text-white">DECISION SUPPORT</h3>
          <span className="text-xs text-blue-400 px-2 py-0.5 bg-blue-500/10 rounded-full border border-blue-500/20">
            APIP
          </span>
        </div>
        <button 
          onClick={handleRefresh}
          className="p-1.5 text-gray-500 hover:text-gray-300 transition-colors rounded-lg hover:bg-dark-bg"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-2 mb-4">
        <div className="bg-dark-bg rounded-lg p-2 text-center">
          <p className="text-lg font-bold text-white">{decisions.length}</p>
          <p className="text-xs text-gray-500">Total</p>
        </div>
        <div className="bg-dark-bg rounded-lg p-2 text-center">
          <p className="text-lg font-bold text-red-400">
            {decisions.filter(d => d.priority === 'CRITICAL').length}
          </p>
          <p className="text-xs text-gray-500">Critical</p>
        </div>
        <div className="bg-dark-bg rounded-lg p-2 text-center">
          <p className="text-lg font-bold text-yellow-400">
            {decisions.filter(d => d.status === 'PENDING').length}
          </p>
          <p className="text-xs text-gray-500">Pending</p>
        </div>
        <div className="bg-dark-bg rounded-lg p-2 text-center">
          <p className="text-lg font-bold text-green-400">
            {decisions.filter(d => d.status === 'COMPLETED').length}
          </p>
          <p className="text-xs text-gray-500">Completed</p>
        </div>
      </div>

      {/* List */}
      <div className="space-y-3 max-h-[400px] overflow-y-auto dark-scrollbar">
        {decisions.map((d) => (
          <div key={d.id} className="bg-dark-bg/50 rounded-lg p-3 border border-dark-border hover:border-blue-500/30 transition-all">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-xs font-mono text-gray-500">{d.id}</span>
                  <span className={`text-xs px-2 py-0.5 rounded-full border ${getPriorityBadge(d.priority)}`}>
                    {d.priority}
                  </span>
                  <span className={`text-xs ${d.status === 'COMPLETED' ? 'text-green-400' : 'text-red-400'}`}>
                    ● {d.status}
                  </span>
                </div>
                <h4 className="text-sm font-medium text-white mt-1">{d.title}</h4>
                <p className="text-xs text-gray-400 mt-0.5">{d.description}</p>
                <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                  <span>Case: {d.case_title}</span>
                  <span>Due: {new Date(d.due_date).toLocaleDateString('id-ID')}</span>
                </div>
                <div className="flex items-center gap-4 mt-1 text-xs text-gray-500">
                  <span>{d.justification?.length || 0} factors</span>
                </div>
              </div>
              <button
                onClick={() => handleReview(d)}
                className="px-3 py-1.5 bg-blue-500/20 hover:bg-blue-500/30 rounded-lg text-xs text-blue-400 transition-colors flex items-center gap-1.5"
              >
                <Eye className="w-3 h-3" />
                Review
              </button>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-3 pt-2 border-t border-dark-border flex justify-between text-xs text-gray-500">
        <span>{decisions.length} decisions</span>
        <span>Updated: {new Date().toLocaleString('id-ID')}</span>
      </div>

      {/* Review Modal */}
      {showReview && selectedDecision && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 animate-fade-in">
          <div className="glass-card w-full max-w-2xl max-h-[80vh] overflow-y-auto p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-white">📋 Review Decision</h3>
              <button onClick={() => setShowReview(false)} className="p-1 text-dark-muted hover:text-white">
                <XCircle className="w-5 h-5" />
              </button>
            </div>

            <div className="space-y-4">
              <div><p className="text-xs text-dark-muted">Title</p><p className="text-sm text-white font-medium">{selectedDecision.title}</p></div>
              <div><p className="text-xs text-dark-muted">Description</p><p className="text-sm text-dark-muted">{selectedDecision.description}</p></div>
              <div className="grid grid-cols-2 gap-4">
                <div><p className="text-xs text-dark-muted">Status</p><span className={`text-sm ${selectedDecision.status === 'COMPLETED' ? 'text-green-400' : 'text-red-400'}`}>● {selectedDecision.status}</span></div>
                <div><p className="text-xs text-dark-muted">Due Date</p><p className="text-sm text-dark-muted">{new Date(selectedDecision.due_date).toLocaleDateString('id-ID')}</p></div>
              </div>
              {selectedDecision.justification.length > 0 && (
                <div>
                  <p className="text-xs text-dark-muted">Justification</p>
                  <div className="mt-2 space-y-2">
                    {selectedDecision.justification.map((f, i) => (
                      <div key={i} className="bg-dark-bg/50 p-2 rounded">
                        <div className="flex justify-between text-sm">
                          <span className="text-white">{f.factor}</span>
                          <span className="text-yellow-400">{f.contribution}%</span>
                        </div>
                        <p className="text-xs text-dark-muted">{f.description}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="flex gap-2 mt-6 pt-4 border-t border-dark-border">
              <button onClick={() => handleAction('approve')} disabled={actionLoading} className="flex-1 px-4 py-2 bg-green-500/20 hover:bg-green-500/30 rounded-lg text-sm text-green-400 transition-colors disabled:opacity-50">
                {actionLoading ? <Loader2 className="w-4 h-4 animate-spin mx-auto" /> : '✅ Approve'}
              </button>
              <button onClick={() => handleAction('reject')} disabled={actionLoading} className="flex-1 px-4 py-2 bg-red-500/20 hover:bg-red-500/30 rounded-lg text-sm text-red-400 transition-colors disabled:opacity-50">
                {actionLoading ? <Loader2 className="w-4 h-4 animate-spin mx-auto" /> : '❌ Reject'}
              </button>
              <button onClick={() => handleAction('request_changes')} disabled={actionLoading} className="flex-1 px-4 py-2 bg-yellow-500/20 hover:bg-yellow-500/30 rounded-lg text-sm text-yellow-400 transition-colors disabled:opacity-50">
                {actionLoading ? <Loader2 className="w-4 h-4 animate-spin mx-auto" /> : '🔄 Request Changes'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default DecisionSupport;
