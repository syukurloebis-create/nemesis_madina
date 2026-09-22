// src/components/Intelligence/FraudSignalExplorer.tsx
//
// Fraud Signal Explorer — Canonical Pattern View
//
// Canonical source: intelligence.fraud.patterns[]
// Backend field: `type` (NOT `pattern_type`)
// Backend values: transaction_anomaly, vendor_collusion, network_anomaly
//
// No client-side categorization into "clusters/packages/methods" —
// that categorization is not part of the backend contract.
//
// Boundary: read-only. Risk Engine v3 untouched.

import React from 'react';
import { AlertTriangle } from 'lucide-react';
import {
  IntelligenceModel,
  FraudPattern,
} from '../../services/intelligenceAdapter';

interface Props {
  intelligence: IntelligenceModel;
}

const severityStyle = (severity: string): string => {
  switch (severity?.toUpperCase()) {
    case 'CRITICAL':
      return 'text-red-400 bg-red-500/10 border-red-500/30';
    case 'HIGH':
      return 'text-orange-400 bg-orange-500/10 border-orange-500/30';
    case 'MEDIUM':
      return 'text-yellow-400 bg-yellow-500/10 border-yellow-500/30';
    case 'LOW':
      return 'text-blue-400 bg-blue-500/10 border-blue-500/30';
    default:
      return 'text-gray-400 bg-gray-500/10 border-gray-500/30';
  }
};

const formatConfidence = (confidence: number): string => {
  if (typeof confidence !== 'number' || isNaN(confidence)) {
    return '—';
  }
  return `${confidence.toFixed(1)}%`;
};

const formatTimestamp = (iso: string): string => {
  if (!iso) return '';
  try {
    const date = new Date(iso);
    if (isNaN(date.getTime())) return '';
    return date.toLocaleString();
  } catch {
    return '';
  }
};

export default function FraudSignalExplorer({ intelligence }: Props) {
  const patterns: FraudPattern[] =
    intelligence?.fraud?.patterns ?? [];

  const totalPatterns =
    intelligence?.fraud?.total_patterns ?? patterns.length;

  const validatedPatterns =
    intelligence?.fraud?.validated_patterns ?? 0;

  return (
    <div className="bg-dark-card border border-dark-border rounded-xl p-6 space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <AlertTriangle className="text-orange-400" />
            Fraud Signal Explorer
          </h2>
          <p className="text-sm text-gray-400">
            Fraud intelligence pattern analysis
          </p>
        </div>
        <div className="text-right">
          <p className="text-xs text-gray-400">Total Patterns</p>
          <p className="text-2xl font-bold text-white">{totalPatterns}</p>
          {validatedPatterns > 0 && (
            <p className="text-xs text-green-400 mt-1">
              {validatedPatterns} validated
            </p>
          )}
        </div>
      </div>

      {/* Pattern list */}
      <div className="space-y-3">
        {patterns.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-gray-500">
              No fraud patterns detected for this case.
            </p>
            <p className="text-xs text-gray-600 mt-2">
              Patterns will appear here when the fraud engine identifies
              suspicious activity.
            </p>
          </div>
        ) : (
          patterns.map((pattern, index) => (
            <div
              key={`${pattern.type}-${index}`}
              className="bg-gray-900 rounded-lg p-4"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span
                      className={`px-2 py-1 rounded text-xs border ${severityStyle(
                        pattern.severity,
                      )}`}
                    >
                      {pattern.severity || 'UNKNOWN'}
                    </span>
                    <span className="text-white text-sm font-medium">
                      {pattern.type || 'unknown_pattern'}
                    </span>
                    {pattern.validated && (
                      <span className="px-2 py-0.5 rounded text-xs bg-green-500/10 text-green-400 border border-green-500/30">
                        Validated
                      </span>
                    )}
                  </div>

                  {pattern.description && (
                    <p className="text-gray-400 text-sm mt-2">
                      {pattern.description}
                    </p>
                  )}

                  {pattern.detectedAt && (
                    <p className="text-xs text-gray-500 mt-2">
                      Detected: {formatTimestamp(pattern.detectedAt)}
                    </p>
                  )}
                </div>

                <div className="text-right shrink-0">
                  <p className="text-xs text-gray-500">Confidence</p>
                  <p className="text-white text-sm font-mono">
                    {formatConfidence(pattern.confidence)}
                  </p>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
