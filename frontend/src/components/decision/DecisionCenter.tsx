import React, { useState } from 'react';
import { CheckCircle, Clock, AlertCircle, ThumbsUp, ThumbsDown, ExternalLink, User, Calendar } from 'lucide-react';

interface DecisionCenterProps {
  caseId: string;
  userId: string;
}

export const DecisionCenter: React.FC<DecisionCenterProps> = ({ caseId, userId }) => {
  const [selectedDecision, setSelectedDecision] = useState<string | null>(null);

  // Mock decisions
  const decisions = [
    {
      id: 'dec-1',
      title: 'Approve Investigation of Vendor X',
      description: 'Suspicious vendor relationships detected in procurement process',
      status: 'PENDING' as const,
      priority: 'HIGH' as const,
      confidence: 85,
      createdAt: new Date(),
      createdByName: 'System AI',
      evidence: ['Transaction patterns', 'Vendor relationships'],
      votes: [
        { vote: 'APPROVE' },
        { vote: 'APPROVE' },
        { vote: 'ABSTAIN' },
      ],
    },
    {
      id: 'dec-2',
      title: 'Implement Monitoring for High-Risk Transactions',
      description: 'Enhanced monitoring needed for identified high-risk patterns',
      status: 'APPROVED' as const,
      priority: 'MEDIUM' as const,
      confidence: 75,
      createdAt: new Date(Date.now() - 86400000),
      approvedAt: new Date(Date.now() - 43200000),
      createdByName: 'System AI',
      evidence: ['Risk patterns', 'Historical data'],
      votes: [
        { vote: 'APPROVE' },
        { vote: 'APPROVE' },
        { vote: 'APPROVE' },
      ],
    },
  ];

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'APPROVED': return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'REJECTED': return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'IMPLEMENTED': return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      case 'PENDING': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      default: return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  const getPriorityBadge = (priority: string) => {
    switch (priority) {
      case 'CRITICAL': return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'HIGH': return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
      case 'MEDIUM': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      default: return 'bg-green-500/20 text-green-400 border-green-500/30';
    }
  };

  return (
    <div className="bg-dark-card border border-dark-border rounded-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-xl font-bold text-white">⚖️ Decision Center</h3>
          <p className="text-dark-muted text-sm">Manage decisions and approvals for this case</p>
        </div>
        <button className="px-4 py-2 bg-primary-500 text-white rounded hover:bg-primary-600 transition-colors">
          + New Decision
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-6 gap-4 mb-6">
        <StatCard label="Total" value="12" icon={AlertCircle} />
        <StatCard label="Pending" value="3" icon={Clock} color="text-yellow-400" />
        <StatCard label="Approved" value="6" icon={ThumbsUp} color="text-green-400" />
        <StatCard label="Implemented" value="2" icon={CheckCircle} color="text-blue-400" />
        <StatCard label="Approval Rate" value="75%" icon={ThumbsUp} color="text-green-400" />
        <StatCard label="Avg Time" value="4.2h" icon={Clock} color="text-cyan-400" />
      </div>

      {/* Decisions List */}
      <div className="space-y-4">
        {decisions.map((decision) => (
          <div
            key={decision.id}
            className={`border rounded-lg p-4 cursor-pointer transition-all ${
              selectedDecision === decision.id
                ? 'border-primary-500/50 bg-primary-500/5'
                : 'border-dark-border hover:border-dark-border/80'
            }`}
            onClick={() => setSelectedDecision(selectedDecision === decision.id ? null : decision.id)}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-1">
                  <span className={`px-2 py-0.5 rounded text-xs font-medium border ${getPriorityBadge(decision.priority)}`}>
                    {decision.priority}
                  </span>
                  <span className={`px-2 py-0.5 rounded text-xs font-medium border ${getStatusBadge(decision.status)}`}>
                    {decision.status}
                  </span>
                </div>
                <h4 className="text-white font-medium">{decision.title}</h4>
                <p className="text-dark-muted text-sm mt-1">{decision.description}</p>
                <div className="flex items-center gap-4 mt-2 text-xs text-dark-muted">
                  <span className="flex items-center gap-1">
                    <User className="w-3 h-3" />
                    {decision.createdByName}
                  </span>
                  <span className="flex items-center gap-1">
                    <Calendar className="w-3 h-3" />
                    {new Date(decision.createdAt).toLocaleDateString()}
                  </span>
                  <span className="text-primary-400">{decision.confidence}% confidence</span>
                  <span>Votes: ✅ {decision.votes.filter(v => v.vote === 'APPROVE').length}</span>
                </div>
              </div>
            </div>

            {selectedDecision === decision.id && (
              <div className="mt-4 pt-4 border-t border-dark-border">
                <div className="flex items-center gap-3">
                  {decision.status === 'PENDING' && (
                    <>
                      <button className="flex items-center gap-2 px-4 py-2 bg-green-500/10 text-green-400 border border-green-500/30 rounded hover:bg-green-500/20 transition-colors">
                        <ThumbsUp className="w-4 h-4" />
                        Approve
                      </button>
                      <button className="flex items-center gap-2 px-4 py-2 bg-red-500/10 text-red-400 border border-red-500/30 rounded hover:bg-red-500/20 transition-colors">
                        <ThumbsDown className="w-4 h-4" />
                        Reject
                      </button>
                    </>
                  )}
                  {decision.status === 'APPROVED' && (
                    <button className="flex items-center gap-2 px-4 py-2 bg-blue-500/10 text-blue-400 border border-blue-500/30 rounded hover:bg-blue-500/20 transition-colors">
                      <CheckCircle className="w-4 h-4" />
                      Implement
                    </button>
                  )}
                  <button className="flex items-center gap-2 px-4 py-2 bg-dark-hover text-dark-muted rounded hover:text-white transition-colors">
                    <ExternalLink className="w-4 h-4" />
                    View Details
                  </button>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

const StatCard: React.FC<{
  label: string;
  value: string | number;
  icon: React.FC<{ className?: string }>;
  color?: string;
}> = ({ label, value, icon: Icon, color = 'text-white' }) => (
  <div className="bg-dark-bg border border-dark-border rounded-lg p-3">
    <div className="flex items-center gap-2 text-dark-muted text-xs">
      <Icon className="w-3 h-3" />
      <span>{label}</span>
    </div>
    <div className={`text-lg font-bold ${color}`}>{value}</div>
  </div>
);

export default DecisionCenter;
