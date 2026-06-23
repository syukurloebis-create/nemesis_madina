import React, { useState } from 'react';
import { AlertTriangle, ChevronDown, ChevronRight, Users, FileText, Shield, Zap } from 'lucide-react';

interface RiskReasoningPanelProps {
  caseId: string;
}

export const RiskReasoningPanel: React.FC<RiskReasoningPanelProps> = ({ caseId }) => {
  const [expandedSteps, setExpandedSteps] = useState<Set<string>>(new Set());

  const toggleStep = (stepId: string) => {
    const newSet = new Set(expandedSteps);
    if (newSet.has(stepId)) {
      newSet.delete(stepId);
    } else {
      newSet.add(stepId);
    }
    setExpandedSteps(newSet);
  };

  const reasoningSteps = [
    {
      id: 'obs-1',
      type: 'OBSERVATION',
      title: 'High Risk Factors Detected',
      description: 'Multiple risk factors identified including financial anomalies and network irregularities',
      confidence: 85,
      evidence: ['Unusual transaction patterns', 'Suspicious vendor relationships'],
    },
    {
      id: 'ana-1',
      type: 'ANALYSIS',
      title: 'Suspicious Network Detected',
      description: 'Analysis reveals interconnected entities with high-risk relationships',
      confidence: 78,
      evidence: ['Entity relationship graph', 'Community detection results'],
    },
    {
      id: 'con-1',
      type: 'CONCLUSION',
      title: 'High Confidence Collusion Pattern',
      description: 'Multiple indicators suggest potential collusion between key actors',
      confidence: 72,
      evidence: ['Bid-rigging patterns', 'Shared procurement history'],
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">🧠 Risk Reasoning Panel</h2>
          <p className="text-dark-muted">Understanding WHY this case has high risk</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-right">
            <div className="text-sm text-dark-muted">Confidence</div>
            <div className="text-lg font-bold text-white">85%</div>
          </div>
          <div className="text-right">
            <div className="text-sm text-dark-muted">Overall Score</div>
            <div className="text-lg font-bold text-primary-400">72%</div>
          </div>
        </div>
      </div>

      <div className="border border-orange-500/50 bg-orange-500/10 rounded-lg p-4">
        <div className="flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 text-orange-500" />
          <div>
            <div className="font-semibold text-white">Risk Level: HIGH</div>
            <div className="text-sm opacity-80">High financial risk detected • Suspicious network patterns found</div>
          </div>
          <div className="ml-auto text-2xl font-bold">72%</div>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-4">
        <div className="bg-dark-card p-3 rounded-lg border border-dark-border">
          <div className="flex items-center gap-2 text-dark-muted text-sm">
            <Users className="w-4 h-4" />
            <span>Entities</span>
          </div>
          <div className="text-xl font-bold text-white">549</div>
        </div>
        <div className="bg-dark-card p-3 rounded-lg border border-dark-border">
          <div className="flex items-center gap-2 text-dark-muted text-sm">
            <Shield className="w-4 h-4" />
            <span>Fraud Patterns</span>
          </div>
          <div className="text-xl font-bold text-white">8</div>
        </div>
        <div className="bg-dark-card p-3 rounded-lg border border-dark-border">
          <div className="flex items-center gap-2 text-dark-muted text-sm">
            <FileText className="w-4 h-4" />
            <span>Evidence</span>
          </div>
          <div className="text-xl font-bold text-white">128</div>
        </div>
        <div className="bg-dark-card p-3 rounded-lg border border-dark-border">
          <div className="flex items-center gap-2 text-dark-muted text-sm">
            <Zap className="w-4 h-4" />
            <span>Collusion Risk</span>
          </div>
          <div className="text-xl font-bold text-white">65%</div>
        </div>
      </div>

      <div className="bg-dark-card rounded-lg border border-dark-border p-4">
        <h3 className="text-lg font-semibold text-white mb-4">🔗 Reasoning Chain</h3>
        <div className="space-y-3">
          {reasoningSteps.map((step) => (
            <div key={step.id} className="border border-dark-border rounded-lg overflow-hidden">
              <button
                onClick={() => toggleStep(step.id)}
                className="w-full flex items-center gap-3 p-3 hover:bg-dark-hover transition-colors text-left"
              >
                {expandedSteps.has(step.id) ? (
                  <ChevronDown className="w-4 h-4 text-dark-muted" />
                ) : (
                  <ChevronRight className="w-4 h-4 text-dark-muted" />
                )}
                <div className={`px-2 py-0.5 rounded text-xs font-medium ${
                  step.type === 'OBSERVATION' ? 'bg-blue-500/20 text-blue-400' :
                  step.type === 'ANALYSIS' ? 'bg-purple-500/20 text-purple-400' :
                  'bg-green-500/20 text-green-400'
                }`}>
                  {step.type}
                </div>
                <span className="text-white font-medium">{step.title}</span>
                <div className="ml-auto text-sm text-dark-muted">
                  {step.confidence}% confidence
                </div>
              </button>
              {expandedSteps.has(step.id) && (
                <div className="p-3 pt-0 border-t border-dark-border mt-0">
                  <p className="text-dark-muted text-sm mb-2">{step.description}</p>
                  {step.evidence.length > 0 && (
                    <div className="bg-dark-bg p-2 rounded text-xs text-dark-muted">
                      <span className="font-medium">Evidence: </span>
                      {step.evidence.join(', ')}
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default RiskReasoningPanel;
