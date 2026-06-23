import React, { useState } from 'react';
import { ThumbsUp, ExternalLink } from 'lucide-react';

interface RecommendationCenterProps {
  caseId: string;
}

export const RecommendationCenter: React.FC<RecommendationCenterProps> = ({ caseId }) => {
  const [filter, setFilter] = useState<'ALL' | 'HIGH' | 'MEDIUM' | 'LOW'>('ALL');
  const [selectedRec, setSelectedRec] = useState<string | null>(null);

  const recommendations = [
    {
      id: 'rec-1',
      title: 'Immediate Investigation Required',
      description: 'High-risk network detected with multiple suspicious entities',
      priority: 'HIGH' as const,
      confidence: 85,
      impact: 80,
      effort: 60,
      actions: ['Review all evidence', 'Conduct stakeholder interviews'],
      category: 'PREVENTIVE' as const,
    },
    {
      id: 'rec-2',
      title: 'Review Vendor Relationships',
      description: 'Suspicious vendor relationships identified in procurement',
      priority: 'MEDIUM' as const,
      confidence: 75,
      impact: 70,
      effort: 50,
      actions: ['Analyze vendor contracts', 'Review payment history'],
      category: 'DETECTIVE' as const,
    },
  ];

  const getPriorityBadge = (priority: string) => {
    switch (priority) {
      case 'HIGH': return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
      case 'MEDIUM': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      default: return 'bg-green-500/20 text-green-400 border-green-500/30';
    }
  };

  const filteredRecommendations = filter === 'ALL' 
    ? recommendations 
    : recommendations.filter(r => r.priority === filter);

  return (
    <div className="bg-dark-card border border-dark-border rounded-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-xl font-bold text-white">💡 Recommendation Center</h3>
          <p className="text-dark-muted text-sm">AI-powered recommendations for this case</p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm text-dark-muted">Filter:</span>
          <div className="flex gap-1">
            {(['ALL', 'HIGH', 'MEDIUM', 'LOW'] as const).map((p) => (
              <button
                key={p}
                onClick={() => setFilter(p)}
                className={`px-3 py-1 rounded text-sm transition-colors ${
                  filter === p 
                    ? 'bg-primary-500/20 text-primary-400 border border-primary-500/30'
                    : 'text-dark-muted hover:text-white hover:bg-dark-hover'
                }`}
              >
                {p}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="space-y-4">
        {filteredRecommendations.map((rec) => (
          <div
            key={rec.id}
            className={`border rounded-lg p-4 cursor-pointer transition-all ${
              selectedRec === rec.id ? 'border-primary-500/50 bg-primary-500/5' : 'border-dark-border hover:border-dark-border/80'
            }`}
            onClick={() => setSelectedRec(selectedRec === rec.id ? null : rec.id)}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className={`px-2 py-0.5 rounded text-xs font-medium border ${getPriorityBadge(rec.priority)}`}>
                    {rec.priority}
                  </span>
                  <span className="text-xs text-dark-muted">{rec.category}</span>
                </div>
                <h4 className="text-white font-medium">{rec.title}</h4>
                <p className="text-dark-muted text-sm mt-1">{rec.description}</p>
              </div>
              <div className="text-right ml-4">
                <div className="text-sm text-dark-muted">Confidence</div>
                <div className="text-lg font-bold text-primary-400">{rec.confidence}%</div>
              </div>
            </div>

            {selectedRec === rec.id && (
              <div className="mt-4 pt-4 border-t border-dark-border">
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div>
                    <div className="text-sm text-dark-muted">Impact</div>
                    <div className="text-white font-medium">{rec.impact}%</div>
                  </div>
                  <div>
                    <div className="text-sm text-dark-muted">Effort Required</div>
                    <div className="text-white font-medium">{rec.effort}%</div>
                  </div>
                </div>
                
                <div className="mb-4">
                  <div className="text-sm text-dark-muted mb-2">Actions</div>
                  <ul className="space-y-1">
                    {rec.actions.map((action, idx) => (
                      <li key={idx} className="text-sm text-white flex items-center gap-2">
                        <span className="w-1.5 h-1.5 bg-primary-400 rounded-full"></span>
                        {action}
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="flex items-center gap-3">
                  <button className="flex items-center gap-2 px-4 py-2 bg-primary-500 text-white rounded hover:bg-primary-600 transition-colors text-sm">
                    <ThumbsUp className="w-4 h-4" />
                    Implement
                  </button>
                  <button className="flex items-center gap-2 px-4 py-2 bg-dark-hover text-dark-muted rounded hover:text-white transition-colors text-sm">
                    <ExternalLink className="w-4 h-4" />
                    Details
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

export default RecommendationCenter;
