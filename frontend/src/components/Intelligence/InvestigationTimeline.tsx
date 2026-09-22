// src/components/Intelligence/InvestigationTimeline.tsx
//
// Investigation Timeline / Activity — Canonical Mixed-Engine Feed
//
// Data source: intelligence.findings.items[]
//   (MIXED-ENGINE observations from fraud_engine, risk_engine,
//    graph_engine, procurement_engine)
//
// NOT the canonical Risk Engine v3 `findings_risk` component.
//
// Backend fields per item:
//   id, source, severity, title, description, confidence,
//   detected_at, metadata
//
// Semantic rule:
//   - If all items have timestamps → "Investigation Timeline"
//   - Otherwise → "Investigation Activity"
//   - Never fabricate chronology or fake timestamps
//
// Boundary: read-only. Risk Engine v3 untouched.

import React, { useMemo, useState } from 'react';
import {
  Clock,
  ChevronDown,
  ChevronRight,
  Activity,
  Tag,
} from 'lucide-react';
import {
  IntelligenceModel,
  InvestigationItem,
} from '../../services/intelligenceAdapter';

interface Props {
  intelligence: IntelligenceModel;
}

const severityStyle = (severity: string) => {
  switch (severity?.toUpperCase()) {
    case 'CRITICAL':
      return {
        badge: 'bg-red-500/20 text-red-400 border-red-500/40',
        dot: 'bg-red-500',
      };
    case 'HIGH':
      return {
        badge: 'bg-orange-500/20 text-orange-400 border-orange-500/40',
        dot: 'bg-orange-500',
      };
    case 'MEDIUM':
      return {
        badge: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/40',
        dot: 'bg-yellow-500',
      };
    case 'LOW':
      return {
        badge: 'bg-blue-500/20 text-blue-400 border-blue-500/40',
        dot: 'bg-blue-500',
      };
    default:
      return {
        badge: 'bg-gray-500/20 text-gray-400 border-gray-500/40',
        dot: 'bg-gray-500',
      };
  }
};

const formatTimestamp = (iso: string | null): string => {
  if (!iso) return '';
  try {
    const date = new Date(iso);
    if (isNaN(date.getTime())) return iso;
    return date.toLocaleString();
  } catch {
    return iso;
  }
};

export default function InvestigationTimeline({ intelligence }: Props) {
  const [expanded, setExpanded] = useState<string | null>(null);

  const items: InvestigationItem[] = useMemo(() => {
    return intelligence?.findings?.items ?? [];
  }, [intelligence]);

  // Semantic: timeline only if every item has a timestamp
  const hasTimestamps =
    items.length > 0 &&
    items.every((item) => item.detectedAt && item.detectedAt.length > 0);

  const viewMode: 'TIMELINE' | 'ACTIVITY' = hasTimestamps
    ? 'TIMELINE'
    : 'ACTIVITY';

  const headerTitle =
    viewMode === 'TIMELINE'
      ? 'Investigation Timeline'
      : 'Investigation Activity';

  const headerSubtitle =
    viewMode === 'TIMELINE'
      ? 'Finding lifecycle and detected events'
      : 'Mixed-engine activity feed (timestamps unavailable)';

  // Empty state
  if (items.length === 0) {
    return (
      <div className="bg-dark-card border border-dark-border rounded-xl p-6 text-gray-400 text-center">
        <p>No investigation activity available for this case.</p>
        <p className="text-xs text-gray-500 mt-2">
          Activity will appear here when fraud, risk, graph, or
          procurement engines produce observations.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-dark-card border border-dark-border rounded-xl p-6 space-y-5">
      {/* HEADER */}
      <div className="flex items-center gap-3">
        <Activity className="text-primary-400" />
        <div>
          <h2 className="text-xl font-bold text-white">{headerTitle}</h2>
          <p className="text-sm text-gray-400">{headerSubtitle}</p>
        </div>
      </div>

      {/* ITEMS */}
      <div className="space-y-4">
        {items.map((item) => {
          const style = severityStyle(item.severity);
          const open = expanded === item.id;
          const hasMetadata =
            item.metadata !== null &&
            typeof item.metadata === 'object' &&
            Object.keys(item.metadata).length > 0;

          return (
            <div
              key={item.id}
              className="border border-gray-700 rounded-xl overflow-hidden"
            >
              <button
                onClick={() => setExpanded(open ? null : item.id)}
                className="w-full flex items-center gap-4 p-4 hover:bg-gray-800/60 transition text-left"
              >
                {open ? (
                  <ChevronDown className="w-5 h-5 text-gray-400 shrink-0" />
                ) : (
                  <ChevronRight className="w-5 h-5 text-gray-400 shrink-0" />
                )}

                <div className={`w-3 h-3 rounded-full shrink-0 ${style.dot}`} />

                <div className="flex-1 min-w-0">
                  <div className="flex gap-3 items-center flex-wrap">
                    <h3 className="text-white font-semibold truncate">
                      {item.title || '(untitled)'}
                    </h3>
                    <span
                      className={`px-2 py-1 rounded border text-xs ${style.badge}`}
                    >
                      {item.severity || 'INFO'}
                    </span>
                  </div>

                  <p className="text-xs text-gray-400 mt-1">
                    {item.source || 'unknown_source'}
                    {item.detectedAt && (
                      <>
                        {' · '}
                        <span className="text-gray-500">
                          {formatTimestamp(item.detectedAt)}
                        </span>
                      </>
                    )}
                  </p>
                </div>

                {typeof item.confidence === 'number' && (
                  <div className="text-right text-xs text-gray-400 shrink-0">
                    <div className="text-gray-500">Confidence</div>
                    <div className="text-white font-mono">
                      {(item.confidence * 100).toFixed(1)}%
                    </div>
                  </div>
                )}
              </button>

              {open && (
                <div className="border-t border-gray-700 p-5 space-y-5">
                  {/* DESCRIPTION */}
                  {item.description && (
                    <div>
                      <p className="text-sm text-gray-300">
                        {item.description}
                      </p>
                    </div>
                  )}

                  {/* TIMESTAMP */}
                  {item.detectedAt && (
                    <div className="flex items-center gap-2 text-sm text-gray-400">
                      <Clock className="w-4 h-4 text-primary-400" />
                      <span className="text-gray-500">Detected:</span>
                      <span className="text-gray-300">
                        {formatTimestamp(item.detectedAt)}
                      </span>
                    </div>
                  )}

                  {/* METADATA */}
                  {hasMetadata && (
                    <div className="bg-gray-900 rounded-lg p-4">
                      <div className="flex items-center gap-2 text-xs text-gray-500 mb-3">
                        <Tag className="w-4 h-4" />
                        Metadata
                      </div>
                      <div className="space-y-1 font-mono text-xs">
                        {Object.entries(item.metadata!).map(([key, value]) => (
                          <div
                            key={key}
                            className="flex justify-between gap-4"
                          >
                            <span className="text-gray-500">{key}</span>
                            <span className="text-gray-300 truncate text-right">
                              {typeof value === 'object'
                                ? JSON.stringify(value)
                                : String(value)}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* ID (technical) */}
                  <div className="text-xs text-gray-600 font-mono break-all">
                    ID: {item.id}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
