// src/components/entity/TrustTimeline.tsx
import React from 'react';
import { TrustPoint } from '../../stores/entityStore';

interface TrustTimelineProps {
  history: TrustPoint[];
}

export const TrustTimeline: React.FC<TrustTimelineProps> = ({ history }) => {
  const maxScore = 100;
  const minScore = 0;

  const getPointColor = (score: number) => {
    if (score >= 70) return 'bg-green-500';
    if (score >= 50) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  if (history.length === 0) {
    return <div className="text-center text-gray-500 py-8">No trust history available</div>;
  }

  return (
    <div className="space-y-4">
      {/* Timeline visualization */}
      <div className="relative pt-6">
        <div className="absolute top-1/2 left-0 right-0 h-0.5 bg-gray-200 -translate-y-1/2"></div>
        <div className="relative flex justify-between">
          {history.map((point, idx) => {
            const leftPercent = (idx / (history.length - 1)) * 100;
            return (
              <div
                key={idx}
                className="absolute"
                style={{ left: `${leftPercent}%`, transform: 'translateX(-50%)' }}
              >
                <div className="text-center">
                  <div
                    className={`w-4 h-4 rounded-full ${getPointColor(point.score)} border-2 border-white shadow`}
                  ></div>
                  <p className="text-xs text-gray-500 mt-2">{new Date(point.timestamp).toLocaleDateString()}</p>
                  <p className="text-sm font-semibold mt-1">{point.score}%</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Events list */}
      <div className="mt-8 space-y-2 max-h-64 overflow-y-auto">
        {history.map((point, idx) => (
          <div key={idx} className="flex items-start gap-3 p-3 hover:bg-gray-50 rounded-lg">
            <div className={`w-2 h-2 mt-2 rounded-full ${getPointColor(point.score)}`}></div>
            <div className="flex-1">
              <div className="flex justify-between items-start">
                <p className="text-sm font-medium text-gray-900">{point.event}</p>
                <span className="text-xs text-gray-500">{new Date(point.timestamp).toLocaleDateString()}</span>
              </div>
              {point.case_id && (
                <p className="text-xs text-gray-400 mt-1">Case: {point.case_id}</p>
              )}
            </div>
            <span className={`text-sm font-semibold ${getPointColor(point.score)}`}>
              {point.score}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};
