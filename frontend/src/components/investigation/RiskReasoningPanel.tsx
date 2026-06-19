// RiskReasoningPanel.tsx - Enhanced Explainable AI
import React, { useState } from 'react';
import { 
  AlertTriangle, 
  Info, 
  ChevronDown, 
  ChevronUp,
  FileText,
  Eye,
  Download,
  RefreshCw,
  Shield,
  TrendingUp,
  Users,
  Building,
  Clock,
  CheckCircle,
  XCircle,
  ExternalLink
} from 'lucide-react';
import { useProvenance } from '../../hooks/useProvenance';
import { RiskContributor } from '../../types/provenance';

interface RiskReasoningPanelProps {
  caseId: string;
  className?: string;
  onInvestigate?: (caseId: string) => void;
  onGenerateReport?: (caseId: string) => void;
}

const RiskFactorItem: React.FC<{ 
  factor: RiskContributor; 
  index: number;
  isExpanded: boolean;
  onToggle: () => void;
}> = ({ factor, index, isExpanded, onToggle }) => {
  const getRiskColor = (contribution: number) => {
    if (contribution >= 40) return 'text-red-400';
    if (contribution >= 20) return 'text-orange-400';
    if (contribution >= 10) return 'text-yellow-400';
    return 'text-green-400';
  };

  const getRiskBarColor = (contribution: number) => {
    if (contribution >= 40) return 'bg-red-500';
    if (contribution >= 20) return 'bg-orange-500';
    if (contribution >= 10) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  return (
    <div className="bg-dark-bg rounded-lg border border-dark-border overflow-hidden">
      <div 
        className="flex items-center justify-between p-3 cursor-pointer hover:bg-dark-card/50 transition-colors"
        onClick={onToggle}
      >
        <div className="flex items-center gap-3 flex-1">
          <span className="text-xs text-gray-500 font-mono">#{index + 1}</span>
          <div className="flex-1">
            <div className="flex items-center gap-2">
              <AlertTriangle className={`w-4 h-4 ${getRiskColor(factor.contribution)}`} />
              <span className="text-sm font-medium text-white capitalize">
                {factor.factor.replace(/_/g, ' ')}
              </span>
              {factor.category && (
                <span className="text-xs px-1.5 py-0.5 bg-gray-700 rounded-full text-gray-400">
                  {factor.category}
                </span>
              )}
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-500">Weight</span>
              <span className="text-xs text-gray-400">{(factor.weight * 100).toFixed(0)}%</span>
            </div>
            <span className={`text-sm font-bold ${getRiskColor(factor.contribution)}`}>
              {factor.contribution}%
            </span>
            {isExpanded ? (
              <ChevronUp className="w-4 h-4 text-gray-500" />
            ) : (
              <ChevronDown className="w-4 h-4 text-gray-500" />
            )}
          </div>
        </div>
      </div>

      {isExpanded && (
        <div className="px-3 pb-3 space-y-2 border-t border-dark-border pt-2">
          <p className="text-sm text-gray-400">{factor.description}</p>
          
          {/* Evidence Trail */}
          {factor.evidence && factor.evidence.length > 0 && (
            <div className="bg-dark-card rounded-lg p-2">
              <p className="text-xs text-gray-500 flex items-center gap-1.5 mb-1.5">
                <FileText className="w-3 h-3" />
                Evidence Trail
              </p>
              <ul className="space-y-1">
                {factor.evidence.map((ev, i) => (
                  <li key={i} className="text-xs text-gray-400 flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-blue-400" />
                    <span>{ev}</span>
                    <button className="text-blue-400 hover:text-blue-300 text-xs ml-auto">
                      View →
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Confidence Score */}
          <div className="flex items-center gap-4 text-xs">
            <div className="flex items-center gap-1.5">
              <Shield className="w-3 h-3 text-gray-500" />
              <span className="text-gray-500">Confidence:</span>
              <span className={`font-medium ${
                factor.score > 70 ? 'text-green-400' :
                factor.score > 40 ? 'text-yellow-400' : 'text-red-400'
              }`}>
                {factor.score}%
              </span>
            </div>
            <div className="flex-1 h-1 bg-gray-700 rounded-full overflow-hidden">
              <div 
                className={`h-full rounded-full ${
                  factor.score > 70 ? 'bg-green-500' :
                  factor.score > 40 ? 'bg-yellow-500' : 'bg-red-500'
                }`}
                style={{ width: `${factor.score}%` }}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export const RiskReasoningPanel: React.FC<RiskReasoningPanelProps> = ({ 
  caseId, 
  className = '',
  onInvestigate,
  onGenerateReport
}) => {
  const { data, loading, error, riskContributors, refetch } = useProvenance(caseId);
  const [expandedIndex, setExpandedIndex] = useState<number | null>(0);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await refetch();
    setIsRefreshing(false);
  };

  const handleInvestigate = () => {
    if (onInvestigate && caseId) {
      onInvestigate(caseId);
    }
  };

  const handleGenerateReport = () => {
    if (onGenerateReport && caseId) {
      onGenerateReport(caseId);
    }
  };

  // Loading State
  if (loading) {
    return (
      <div className={`bg-dark-card rounded-lg border border-dark-border p-4 ${className}`}>
        <div className="animate-pulse">
          <div className="flex items-center justify-between mb-4">
            <div className="h-6 bg-gray-700 rounded w-1/3" />
            <div className="h-4 bg-gray-700 rounded w-1/4" />
          </div>
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <div key={i} className="bg-dark-bg rounded-lg p-3 border border-dark-border">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3 flex-1">
                    <div className="h-5 w-5 bg-gray-700 rounded" />
                    <div className="h-4 bg-gray-700 rounded w-1/3" />
                  </div>
                  <div className="h-5 w-12 bg-gray-700 rounded" />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // Error State
  if (error) {
    return (
      <div className={`bg-red-500/10 border border-red-500/30 rounded-lg p-4 ${className}`}>
        <div className="flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-red-400">Error Loading Risk Reasoning</p>
            <p className="text-sm text-red-400/70 mt-1">{error}</p>
            <button 
              onClick={handleRefresh}
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

  // No Data State
  if (!data || !riskContributors.length) {
    return (
      <div className={`bg-gray-500/10 border border-gray-500/30 rounded-lg p-4 text-center ${className}`}>
        <div className="flex flex-col items-center gap-2">
          <Info className="w-8 h-8 text-gray-500" />
          <p className="text-sm text-gray-400">Tidak ada data risk reasoning untuk kasus ini</p>
          <p className="text-xs text-gray-500">Pastikan kasus memiliki data provenance yang lengkap</p>
        </div>
      </div>
    );
  }

  // Main Render
  const riskLevel = data.risk_level || 'MEDIUM';
  const riskScore = data.risk_score || 0;

  const getRiskLevelColor = (level: string) => {
    switch(level) {
      case 'CRITICAL': return 'text-red-400 bg-red-500/20 border-red-500/30';
      case 'HIGH': return 'text-orange-400 bg-orange-500/20 border-orange-500/30';
      case 'MEDIUM': return 'text-yellow-400 bg-yellow-500/20 border-yellow-500/30';
      default: return 'text-green-400 bg-green-500/20 border-green-500/30';
    }
  };

  const getRiskLevelIcon = (level: string) => {
    switch(level) {
      case 'CRITICAL':
      case 'HIGH': return <AlertTriangle className="w-5 h-5" />;
      default: return <Info className="w-5 h-5" />;
    }
  };

  return (
    <div className={`bg-dark-card rounded-lg border border-dark-border ${className}`}>
      {/* Header */}
      <div className="p-4 border-b border-dark-border">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-lg">🧠</span>
            <h3 className="text-sm font-semibold text-white">RISK REASONING</h3>
            <span className="text-xs text-blue-400 px-2 py-0.5 bg-blue-500/10 rounded-full border border-blue-500/20">
              Explainable AI
            </span>
          </div>
          <div className="flex items-center gap-2">
            <button 
              onClick={handleRefresh}
              disabled={isRefreshing}
              className="p-1.5 text-gray-500 hover:text-gray-300 transition-colors rounded-lg hover:bg-dark-bg"
            >
              <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
            </button>
            <button 
              onClick={handleGenerateReport}
              className="flex items-center gap-1.5 text-xs text-blue-400 hover:text-blue-300 transition-colors px-2 py-1 border border-blue-400/30 rounded-lg hover:bg-blue-500/10"
            >
              <FileText className="w-3 h-3" />
              Report
            </button>
          </div>
        </div>

        {/* Case Info */}
        <div className="flex flex-wrap items-center gap-4 mt-3 text-sm">
          <span className="text-gray-400">{data.case_title}</span>
          <span className="w-px h-4 bg-dark-border" />
          <span className={`text-xs px-2 py-0.5 rounded-full border ${getRiskLevelColor(riskLevel)} flex items-center gap-1.5`}>
            {getRiskLevelIcon(riskLevel)}
            {riskLevel}
          </span>
          <span className="text-xs text-gray-500">Stage: {data.workflow_stage}</span>
        </div>
      </div>

      {/* Risk Score */}
      <div className="p-4 border-b border-dark-border bg-dark-bg">
        <div className="flex items-center gap-4">
          <div className="flex items-baseline gap-1">
            <span className="text-3xl font-bold text-red-400">{riskScore}</span>
            <span className="text-sm text-gray-500">/ 100</span>
          </div>
          <div className="flex-1">
            <div className="flex justify-between text-xs text-gray-500 mb-1">
              <span>Risk Score</span>
              <span>{riskLevel}</span>
            </div>
            <div className="w-full h-2 bg-gray-700 rounded-full overflow-hidden">
              <div 
                className={`h-full rounded-full ${
                  riskScore >= 80 ? 'bg-red-500' :
                  riskScore >= 60 ? 'bg-orange-500' :
                  riskScore >= 40 ? 'bg-yellow-500' : 'bg-green-500'
                }`}
                style={{ width: `${Math.min(riskScore, 100)}%` }}
              />
            </div>
            <div className="flex justify-between text-xs text-gray-600 mt-1">
              <span>0</span>
              <span>50</span>
              <span>100</span>
            </div>
          </div>
        </div>
      </div>

      {/* Risk Factors */}
      <div className="p-4 space-y-3">
        <div className="flex items-center justify-between">
          <h4 className="text-xs font-medium text-gray-400 uppercase tracking-wider">
            Risk Contributors
          </h4>
          <span className="text-xs text-gray-500">{riskContributors.length} factors</span>
        </div>

        {riskContributors.map((factor, index) => (
          <RiskFactorItem
            key={index}
            factor={factor}
            index={index}
            isExpanded={expandedIndex === index}
            onToggle={() => setExpandedIndex(expandedIndex === index ? null : index)}
          />
        ))}
      </div>

      {/* Actions */}
      <div className="p-4 border-t border-dark-border">
        <div className="flex gap-3">
          <button 
            onClick={handleInvestigate}
            className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-red-500/20 hover:bg-red-500/30 rounded-lg text-sm text-red-400 transition-colors border border-red-500/20"
          >
            <Eye className="w-4 h-4" />
            Investigate Case
          </button>
          <button 
            onClick={handleGenerateReport}
            className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-blue-500/20 hover:bg-blue-500/30 rounded-lg text-sm text-blue-400 transition-colors border border-blue-500/20"
          >
            <Download className="w-4 h-4" />
            Generate Report
          </button>
        </div>
        <div className="flex items-center justify-between mt-3 text-xs text-gray-500">
          <span>Last updated: {new Date(data.timestamp).toLocaleString('id-ID')}</span>
          <span className="flex items-center gap-1">
            <CheckCircle className="w-3 h-3 text-green-400" />
            Verified by AI
          </span>
        </div>
      </div>
    </div>
  );
};

export default RiskReasoningPanel;
