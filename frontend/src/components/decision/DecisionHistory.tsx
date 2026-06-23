import React from 'react';
import { Clock, CheckCircle, XCircle, AlertTriangle, User, Calendar } from 'lucide-react';

interface DecisionHistoryProps {
  decisions?: any[];
  limit?: number;
}

export const DecisionHistory: React.FC<DecisionHistoryProps> = ({ decisions = [], limit = 20 }) => {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'APPROVED': return <CheckCircle className="w-5 h-5 text-green-400" />;
      case 'REJECTED': return <XCircle className="w-5 h-5 text-red-400" />;
      case 'IMPLEMENTED': return <CheckCircle className="w-5 h-5 text-blue-400" />;
      case 'ESCALATED': return <AlertTriangle className="w-5 h-5 text-purple-400" />;
      default: return <Clock className="w-5 h-5 text-yellow-400" />;
    }
  };

  const mockHistory = [
    {
      id: 'hist-1',
      title: 'Investigation Approved',
      description: 'Case investigation approved by supervisor',
      status: 'APPROVED',
      priority: 'HIGH',
      createdAt: new Date(Date.now() - 3600000),
      createdByName: 'John Doe',
      confidence: 85,
    },
    {
      id: 'hist-2',
      title: 'Evidence Review Completed',
      description: 'All evidence reviewed and verified',
      status: 'IMPLEMENTED',
      priority: 'MEDIUM',
      createdAt: new Date(Date.now() - 7200000),
      createdByName: 'Jane Smith',
      confidence: 90,
    },
  ];

  const history = decisions.length > 0 ? decisions : mockHistory;

  return (
    <div className="bg-dark-card border border-dark-border rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white">📜 Decision History</h3>
        <span className="text-sm text-dark-muted">{history.length} total decisions</span>
      </div>

      <div className="relative">
        <div className="absolute left-5 top-0 bottom-0 w-0.5 bg-dark-border" />

        <div className="space-y-6">
          {history.slice(0, limit).map((decision) => (
            <div key={decision.id} className="relative flex gap-4">
              <div className="flex-shrink-0 w-10 h-10 rounded-full bg-dark-bg border-2 border-dark-border flex items-center justify-center z-10">
                {getStatusIcon(decision.status)}
              </div>

              <div className="flex-1">
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <h4 className="text-white font-medium">{decision.title}</h4>
                      <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                        decision.priority === 'HIGH' ? 'bg-orange-500/20 text-orange-400' :
                        decision.priority === 'MEDIUM' ? 'bg-yellow-500/20 text-yellow-400' :
                        'bg-green-500/20 text-green-400'
                      }`}>
                        {decision.priority}
                      </span>
                    </div>
                    <p className="text-dark-muted text-sm">{decision.description}</p>
                  </div>
                  <div className="text-right text-sm">
                    <div className={`font-medium ${
                      decision.status === 'APPROVED' ? 'text-green-400' :
                      decision.status === 'REJECTED' ? 'text-red-400' :
                      decision.status === 'IMPLEMENTED' ? 'text-blue-400' :
                      'text-yellow-400'
                    }`}>
                      {decision.status}
                    </div>
                    <div className="text-dark-muted text-xs">
                      {new Date(decision.createdAt).toLocaleString()}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-4 mt-2 text-xs text-dark-muted">
                  <span className="flex items-center gap-1">
                    <User className="w-3 h-3" />
                    {decision.createdByName}
                  </span>
                  <span className="flex items-center gap-1">
                    <Calendar className="w-3 h-3" />
                    {new Date(decision.createdAt).toLocaleDateString()}
                  </span>
                  <span className="text-primary-400">
                    {decision.confidence}% confidence
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default DecisionHistory;
