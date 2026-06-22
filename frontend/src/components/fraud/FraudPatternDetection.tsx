// src/components/fraud/FraudPatternDetection.tsx
import React, { useState } from 'react';
import { useFraudPatterns } from '../../hooks/useFraudPatterns';
import type { FraudSeverity, FraudStatus, FraudPattern } from '../../types';

interface FraudPatternDetectionProps {
  caseId?: string;
  onInvestigate?: (patternId: string) => void;
  className?: string;
}

const severityConfig: Record<FraudSeverity, { label: string; color: string; bg: string; border: string }> = {
  CRITICAL: { label: 'Critical', color: 'text-red-400', bg: 'bg-red-500/10', border: 'border-red-500/30' },
  HIGH: { label: 'High', color: 'text-orange-400', bg: 'bg-orange-500/10', border: 'border-orange-500/30' },
  MEDIUM: { label: 'Medium', color: 'text-yellow-400', bg: 'bg-yellow-500/10', border: 'border-yellow-500/30' },
  LOW: { label: 'Low', color: 'text-green-400', bg: 'bg-green-500/10', border: 'border-green-500/30' },
};

const statusConfig: Record<FraudStatus, { label: string; color: string }> = {
  ACTIVE: { label: 'Active', color: 'text-blue-400' },
  INVESTIGATING: { label: 'Investigating', color: 'text-purple-400' },
  RESOLVED: { label: 'Resolved', color: 'text-green-400' },
  FALSE_POSITIVE: { label: 'False Positive', color: 'text-gray-400' },
};

export const FraudPatternDetection: React.FC<FraudPatternDetectionProps> = ({
  caseId,
  onInvestigate,
  className = '',
}) => {
  const { patterns, loading, error, refetch } = useFraudPatterns({ caseId });
  const [filterSeverity, setFilterSeverity] = useState<FraudSeverity | 'ALL'>('ALL');

  if (loading) return <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto" />;
  if (error) return <div className="text-red-400">Error: {error}</div>;

  const filtered = filterSeverity === 'ALL' ? patterns : patterns.filter((p) => p.severity === filterSeverity);
  if (filtered.length === 0) return <div className="text-gray-400 text-center py-8">No fraud patterns detected</div>;

  return (
    <div className={`space-y-4 ${className}`}>
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold text-white">🔍 Fraud Patterns</h3>
        <select
          value={filterSeverity}
          onChange={(e) => setFilterSeverity(e.target.value as FraudSeverity | 'ALL')}
          className="bg-dark-card text-white rounded-lg px-3 py-1 border border-gray-700"
        >
          <option value="ALL">All</option>
          <option value="CRITICAL">Critical</option>
          <option value="HIGH">High</option>
          <option value="MEDIUM">Medium</option>
          <option value="LOW">Low</option>
        </select>
      </div>

      {filtered.map((pattern: FraudPattern) => (
        <div key={pattern.id} className={`bg-dark-card rounded-xl shadow-lg border p-4 ${severityConfig[pattern.severity]?.border || 'border-gray-700/50'}`}>
          <div className="flex justify-between items-start">
            <div>
              <h4 className="text-white font-medium">{pattern.name}</h4>
              <p className="text-sm text-gray-400">{pattern.description}</p>
              <div className="flex gap-4 mt-2 text-sm">
                <span className="text-gray-400">Confidence: <span className="text-white">{pattern.confidence}%</span></span>
                <span className="text-gray-400">Status: <span className={statusConfig[pattern.status]?.color}>{statusConfig[pattern.status]?.label}</span></span>
              </div>
            </div>
            <button onClick={() => onInvestigate?.(pattern.id)} className="px-4 py-1 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700">Investigate</button>
          </div>
        </div>
      ))}
    </div>
  );
};

export default FraudPatternDetection;
