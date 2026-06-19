// FraudDetectionPanel.tsx - AI Fraud Detection
import React from 'react';
import { AlertTriangle, ChevronRight, CheckCircle, XCircle } from 'lucide-react';

interface FraudDetectionPanelProps {
  cases: any[];
}

export const FraudDetectionPanel: React.FC<FraudDetectionPanelProps> = ({ cases }) => {
  const anomalies = [
    {
      title: 'Suspicious Procurement Pattern',
      confidence: 92,
      indicators: [
        'Same vendor repeatedly selected',
        'Abnormal price similarity',
        'Hidden relationship detected',
        'Timeline anomaly'
      ],
      severity: 'HIGH'
    },
    {
      title: 'Conflict of Interest Detected',
      confidence: 78,
      indicators: [
        'Family relationship between vendor and official',
        'Unusual approval pattern',
        'Multiple contracts without competition'
      ],
      severity: 'MEDIUM'
    }
  ];

  return (
    <div className="bg-dark-card rounded-lg border border-dark-border p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-white">🚨 AI FRAUD DETECTION</h3>
        <span className="text-xs text-red-400 animate-pulse">● LIVE</span>
      </div>

      <div className="space-y-3">
        {anomalies.map((anomaly, idx) => (
          <div key={idx} className="bg-red-500/5 border border-red-500/20 rounded-lg p-3">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <AlertTriangle className={`w-4 h-4 ${anomaly.severity === 'HIGH' ? 'text-red-400' : 'text-yellow-400'}`} />
                  <span className="text-sm font-medium text-white">{anomaly.title}</span>
                </div>
                <div className="flex items-center gap-2 mt-1">
                  <span className="text-xs text-gray-400">Confidence:</span>
                  <span className={`text-xs font-bold ${anomaly.confidence > 80 ? 'text-red-400' : 'text-yellow-400'}`}>
                    {anomaly.confidence}%
                  </span>
                </div>
                <div className="mt-2 space-y-1">
                  {anomaly.indicators.map((indicator, i) => (
                    <div key={i} className="flex items-center gap-1.5 text-xs text-gray-400">
                      <CheckCircle className="w-3 h-3 text-green-400" />
                      <span>{indicator}</span>
                    </div>
                  ))}
                </div>
              </div>
              <div className="flex flex-col items-end gap-2">
                <span className={`text-xs px-2 py-0.5 rounded-full ${anomaly.severity === 'HIGH' ? 'bg-red-500/20 text-red-400' : 'bg-yellow-500/20 text-yellow-400'}`}>
                  {anomaly.severity}
                </span>
                <button className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1">
                  Investigate <ChevronRight className="w-3 h-3" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default FraudDetectionPanel;
