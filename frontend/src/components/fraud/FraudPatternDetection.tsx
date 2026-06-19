// FraudPatternDetection.tsx - WITH WORKING FILTERS
import React, { useState, useMemo } from 'react';
import { 
  AlertTriangle, 
  TrendingUp, 
  TrendingDown, 
  Minus, 
  Eye, 
  RefreshCw, 
  Filter, 
  Clock, 
  CheckCircle, 
  XCircle, 
  Zap, 
  Activity,
  Loader2
} from 'lucide-react';
import { useFraudPatterns } from '../../hooks/useFraudPatterns';
import { FraudSeverity } from '../../types/fraud';
import ConfidenceScore from './ConfidenceScore';

interface FraudPatternDetectionProps {
  className?: string;
  onInvestigate?: (patternId: string) => void;
  onResolve?: (patternId: string) => void;
}

const severityConfig: Record<FraudSeverity, { label: string; color: string; bg: string; border: string }> = {
  CRITICAL: {
    label: 'CRITICAL',
    color: 'text-red-400',
    bg: 'bg-red-500/10',
    border: 'border-red-500/30'
  },
  HIGH: {
    label: 'HIGH',
    color: 'text-orange-400',
    bg: 'bg-orange-500/10',
    border: 'border-orange-500/30'
  },
  MEDIUM: {
    label: 'MEDIUM',
    color: 'text-yellow-400',
    bg: 'bg-yellow-500/10',
    border: 'border-yellow-500/30'
  },
  LOW: {
    label: 'LOW',
    color: 'text-green-400',
    bg: 'bg-green-500/10',
    border: 'border-green-500/30'
  }
};

const statusConfig: Record<string, { label: string; color: string; icon: React.ReactNode }> = {
  ACTIVE: {
    label: 'Active',
    color: 'text-red-400',
    icon: <Zap className="w-3 h-3" />
  },
  INVESTIGATING: {
    label: 'Investigating',
    color: 'text-yellow-400',
    icon: <Clock className="w-3 h-3" />
  },
  RESOLVED: {
    label: 'Resolved',
    color: 'text-green-400',
    icon: <CheckCircle className="w-3 h-3" />
  },
  FALSE_POSITIVE: {
    label: 'False Positive',
    color: 'text-gray-400',
    icon: <XCircle className="w-3 h-3" />
  }
};

const PatternCard: React.FC<{ 
  pattern: any; 
  onInvestigate: (id: string) => Promise<void>;
  onResolve: (id: string) => Promise<void>;
}> = ({ pattern, onInvestigate, onResolve }) => {
  const [expanded, setExpanded] = useState(false);
  const [loading, setLoading] = useState<string | null>(null);
  const severity = severityConfig[pattern.severity] || severityConfig.MEDIUM;
  const status = statusConfig[pattern.status] || statusConfig.ACTIVE;

  const handleInvestigate = async () => {
    setLoading('investigate');
    await onInvestigate(pattern.id);
    setLoading(null);
  };

  const handleResolve = async () => {
    setLoading('resolve');
    await onResolve(pattern.id);
    setLoading(null);
  };

  return (
    <div className={`bg-dark-card rounded-lg border ${severity.border} p-4 hover:border-blue-500/50 transition-all`}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs font-mono text-gray-500">{pattern.id?.slice(0, 8)}</span>
            <span className={`text-xs px-2 py-0.5 rounded-full ${severity.bg} ${severity.color} border ${severity.border}`}>
              {severity.label}
            </span>
            <span className={`text-xs px-2 py-0.5 rounded-full flex items-center gap-1 ${status.color} bg-gray-700/30`}>
              {status.icon}
              {status.label}
            </span>
            <span className="text-xs text-gray-500">{pattern.category}</span>
          </div>

          <h4 className="text-sm font-medium text-white mt-1">{pattern.name}</h4>
          <p className="text-xs text-gray-400 mt-0.5">{pattern.description}</p>

          <div className="flex items-center gap-4 mt-2 text-xs">
            <div className="flex items-center gap-1">
              <span className="text-gray-500">Confidence:</span>
              <ConfidenceScore score={pattern.confidence} size="sm" showLabel={false} />
            </div>
            <div className="flex items-center gap-1">
              <span className="text-gray-500">Trend:</span>
              {pattern.trend === 'RISING' && <TrendingUp className="w-3 h-3 text-red-400" />}
              {pattern.trend === 'DECLINING' && <TrendingDown className="w-3 h-3 text-green-400" />}
              {pattern.trend === 'STABLE' && <Minus className="w-3 h-3 text-yellow-400" />}
              <span className="text-gray-400">{pattern.trend}</span>
            </div>
            <div className="flex items-center gap-1">
              <span className="text-gray-500">Cases:</span>
              <span className="text-gray-400">{pattern.cases?.length || 0}</span>
            </div>
            <div className="flex items-center gap-1">
              <span className="text-gray-500">Evidence:</span>
              <span className="text-gray-400">{pattern.evidence_count || 0}</span>
            </div>
          </div>

          {pattern.affected_entities && pattern.affected_entities.length > 0 && (
            <div className="flex items-center gap-1 mt-2">
              <span className="text-xs text-gray-500">Entities:</span>
              <div className="flex flex-wrap gap-1">
                {pattern.affected_entities.slice(0, 3).map((entity: string, i: number) => (
                  <span key={i} className="text-xs text-gray-400 bg-dark-bg px-1.5 py-0.5 rounded">
                    {entity}
                  </span>
                ))}
                {pattern.affected_entities.length > 3 && (
                  <span className="text-xs text-gray-500">+{pattern.affected_entities.length - 3} more</span>
                )}
              </div>
            </div>
          )}

          {pattern.indicators && pattern.indicators.length > 0 && (
            <button
              onClick={() => setExpanded(!expanded)}
              className="mt-2 text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1"
            >
              {expanded ? 'Hide' : 'Show'} Indicators
              <span className={`transition-transform ${expanded ? 'rotate-180' : ''}`}>▼</span>
            </button>
          )}

          {expanded && pattern.indicators && (
            <div className="mt-2 space-y-1">
              {pattern.indicators.map((indicator: any, i: number) => (
                <div key={i} className="flex items-center gap-2 text-xs bg-dark-bg p-1.5 rounded">
                  <span className={`w-1.5 h-1.5 rounded-full ${indicator.detected ? 'bg-green-400' : 'bg-gray-600'}`} />
                  <span className="text-gray-300">{indicator.name}</span>
                  <span className="text-gray-500 ml-auto">{indicator.confidence}%</span>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="flex flex-col gap-2 ml-4">
          {pattern.status !== 'INVESTIGATING' && pattern.status !== 'RESOLVED' && (
            <button
              onClick={handleInvestigate}
              disabled={!!loading}
              className="px-3 py-1.5 bg-yellow-500/20 hover:bg-yellow-500/30 rounded-lg text-xs text-yellow-400 transition-colors flex items-center gap-1.5"
            >
              {loading === 'investigate' ? (
                <Loader2 className="w-3 h-3 animate-spin" />
              ) : (
                <Eye className="w-3 h-3" />
              )}
              Investigate
            </button>
          )}
          {pattern.status === 'INVESTIGATING' && (
            <button
              onClick={handleResolve}
              disabled={!!loading}
              className="px-3 py-1.5 bg-green-500/20 hover:bg-green-500/30 rounded-lg text-xs text-green-400 transition-colors flex items-center gap-1.5"
            >
              {loading === 'resolve' ? (
                <Loader2 className="w-3 h-3 animate-spin" />
              ) : (
                <CheckCircle className="w-3 h-3" />
              )}
              Resolve
            </button>
          )}
        </div>
      </div>

      <div className="flex items-center gap-4 mt-3 pt-2 border-t border-dark-border text-xs text-gray-500">
        <span>Detected: {new Date(pattern.detected_at).toLocaleString('id-ID')}</span>
        <span>Updated: {new Date(pattern.updated_at).toLocaleString('id-ID')}</span>
      </div>
    </div>
  );
};

export const FraudPatternDetection: React.FC<FraudPatternDetectionProps> = ({
  className = '',
  onInvestigate,
  onResolve
}) => {
  const { patterns, summary, loading, error, fetchPatterns, updateStatus } = useFraudPatterns();
  const [filterSeverity, setFilterSeverity] = useState<FraudSeverity | 'ALL'>('ALL');
  const [filterStatus, setFilterStatus] = useState<string | 'ALL'>('ALL');

  // ============================================================
  // FILTER LOGIC - MEMOIZED
  // ============================================================
  const filteredPatterns = useMemo(() => {
    if (!patterns || patterns.length === 0) return [];
    
    return patterns.filter((pattern: any) => {
      // Filter by severity
      if (filterSeverity !== 'ALL' && pattern.severity !== filterSeverity) {
        return false;
      }
      
      // Filter by status
      if (filterStatus !== 'ALL' && pattern.status !== filterStatus) {
        return false;
      }
      
      return true;
    });
  }, [patterns, filterSeverity, filterStatus]);

  const handleInvestigate = async (id: string) => {
    try {
      await updateStatus(id, 'INVESTIGATING');
      if (onInvestigate) {
        onInvestigate(id);
      }
      await fetchPatterns();
    } catch (error) {
      console.error('Error investigating pattern:', error);
      alert('❌ Failed to investigate pattern');
    }
  };

  const handleResolve = async (id: string) => {
    try {
      await updateStatus(id, 'RESOLVED');
      if (onResolve) {
        onResolve(id);
      }
      await fetchPatterns();
    } catch (error) {
      console.error('Error resolving pattern:', error);
      alert('❌ Failed to resolve pattern');
    }
  };

  if (loading) {
    return (
      <div className={`glass-card p-4 ${className}`}>
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-gray-700 rounded w-1/3" />
          <div className="grid grid-cols-4 gap-2">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="h-16 bg-gray-700 rounded" />
            ))}
          </div>
          <div className="space-y-2">
            {[1, 2, 3].map(i => (
              <div key={i} className="h-24 bg-gray-700 rounded" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`bg-red-500/10 border border-red-500/30 rounded-lg p-4 ${className}`}>
        <div className="flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-red-400">Error Loading Fraud Patterns</p>
            <p className="text-sm text-red-400/70 mt-1">{error}</p>
            <button 
              onClick={fetchPatterns}
              className="mt-2 text-sm text-red-400 hover:text-red-300 flex items-center gap-1.5"
            >
              <RefreshCw className="w-3 h-3" />
              Retry
            </button>
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
          <span className="text-lg">🔍</span>
          <h3 className="text-sm font-semibold text-white">FRAUD PATTERN DETECTION</h3>
          <span className="text-xs text-red-400 px-2 py-0.5 bg-red-500/10 rounded-full border border-red-500/20 animate-pulse">
            ● LIVE
          </span>
        </div>
        <button 
          onClick={fetchPatterns}
          className="p-1.5 text-gray-500 hover:text-gray-300 transition-colors rounded-lg hover:bg-dark-bg"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* Summary Stats */}
      {summary && (
        <div className="grid grid-cols-5 gap-2 mb-3">
          <div className="bg-dark-bg rounded-lg p-2 text-center">
            <p className="text-lg font-bold text-white">{summary.total || 0}</p>
            <p className="text-xs text-gray-500">Total</p>
          </div>
          <div className="bg-dark-bg rounded-lg p-2 text-center">
            <p className="text-lg font-bold text-red-400">{summary.by_severity?.CRITICAL || 0}</p>
            <p className="text-xs text-gray-500">Critical</p>
          </div>
          <div className="bg-dark-bg rounded-lg p-2 text-center">
            <p className="text-lg font-bold text-orange-400">{summary.by_severity?.HIGH || 0}</p>
            <p className="text-xs text-gray-500">High</p>
          </div>
          <div className="bg-dark-bg rounded-lg p-2 text-center">
            <p className="text-lg font-bold text-yellow-400">{summary.by_severity?.MEDIUM || 0}</p>
            <p className="text-xs text-gray-500">Medium</p>
          </div>
          <div className="bg-dark-bg rounded-lg p-2 text-center">
            <p className="text-lg font-bold text-green-400">{summary.by_severity?.LOW || 0}</p>
            <p className="text-xs text-gray-500">Low</p>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="flex flex-wrap gap-2 mb-3">
        <div className="flex items-center gap-1.5">
          <Filter className="w-3 h-3 text-gray-500" />
          <select
            value={filterSeverity}
            onChange={(e) => {
              setFilterSeverity(e.target.value as FraudSeverity | 'ALL');
            }}
            className="bg-dark-bg border border-dark-border rounded-lg px-2 py-1 text-xs text-gray-300 focus:outline-none focus:border-blue-500/50"
          >
            <option value="ALL">All Severity</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>
        </div>
        <div className="flex items-center gap-1.5">
          <Clock className="w-3 h-3 text-gray-500" />
          <select
            value={filterStatus}
            onChange={(e) => {
              setFilterStatus(e.target.value);
            }}
            className="bg-dark-bg border border-dark-border rounded-lg px-2 py-1 text-xs text-gray-300 focus:outline-none focus:border-blue-500/50"
          >
            <option value="ALL">All Status</option>
            <option value="ACTIVE">Active</option>
            <option value="INVESTIGATING">Investigating</option>
            <option value="RESOLVED">Resolved</option>
            <option value="FALSE_POSITIVE">False Positive</option>
          </select>
        </div>
        <span className="text-xs text-gray-500 ml-auto">{filteredPatterns.length} patterns</span>
        {(filterSeverity !== 'ALL' || filterStatus !== 'ALL') && (
          <button
            onClick={() => {
              setFilterSeverity('ALL');
              setFilterStatus('ALL');
            }}
            className="text-xs text-blue-400 hover:text-blue-300"
          >
            Clear Filters
          </button>
        )}
      </div>

      {/* Patterns List */}
      <div className="space-y-3 max-h-[500px] overflow-y-auto dark-scrollbar">
        {filteredPatterns.length === 0 ? (
          <div className="text-center py-8 text-gray-400">
            <p>Tidak ada pattern sesuai filter</p>
            {(filterSeverity !== 'ALL' || filterStatus !== 'ALL') && (
              <button
                onClick={() => {
                  setFilterSeverity('ALL');
                  setFilterStatus('ALL');
                }}
                className="mt-2 text-sm text-blue-400 hover:text-blue-300"
              >
                Clear Filters
              </button>
            )}
          </div>
        ) : (
          filteredPatterns.map((pattern: any) => (
            <PatternCard
              key={pattern.id}
              pattern={pattern}
              onInvestigate={handleInvestigate}
              onResolve={handleResolve}
            />
          ))
        )}
      </div>

      {/* Footer */}
      <div className="mt-3 pt-2 border-t border-dark-border flex justify-between text-xs text-gray-500">
        <span>AI-powered fraud detection</span>
        <span>Updated: {new Date().toLocaleString('id-ID')}</span>
      </div>
    </div>
  );
};

export default FraudPatternDetection;
