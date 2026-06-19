// EnhancedNetworkGraph.tsx - Network Graph dengan Filter & Collusion Detection
import React, { useCallback, useRef } from 'react';
import NetworkGraph from './NetworkGraph';
import NetworkFilters from './filters/NetworkFilters';
import useNetworkFilters from './hooks/useNetworkFilters';
import { AlertTriangle, Shield, Users } from 'lucide-react';

interface EnhancedNetworkGraphProps {
  actors: any[];
  height?: number;
  className?: string;
  onNodeClick?: (actor: any) => void;
  onExport?: () => void;
}

export const EnhancedNetworkGraph: React.FC<EnhancedNetworkGraphProps> = ({
  actors,
  height = 450,
  className = '',
  onNodeClick,
  onExport
}) => {
  const {
    searchQuery,
    riskFilter,
    communityFilter,
    filteredActors,
    communities,
    setSearchQuery,
    setRiskFilter,
    setCommunityFilter,
    resetFilters
  } = useNetworkFilters(actors);

  const [isLoading, setIsLoading] = React.useState(false);

  // Calculate statistics
  const stats = React.useMemo(() => {
    const total = actors.length;
    const filtered = filteredActors.length;
    const highRisk = filteredActors.filter(a => (a.risk_score || 0) >= 80).length;
    const collusion = filteredActors.filter(a => (a.connections || 0) > 2).length;
    return { total, filtered, highRisk, collusion };
  }, [actors, filteredActors]);

  const handleRefresh = useCallback(() => {
    setIsLoading(true);
    setTimeout(() => {
      resetFilters();
      setIsLoading(false);
    }, 500);
  }, [resetFilters]);

  const handleExport = useCallback(() => {
    if (onExport) {
      onExport();
    }
    // Default export: download as JSON
    const dataStr = JSON.stringify({ actors: filteredActors, stats }, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `network-data-${new Date().toISOString().slice(0,10)}.json`;
    link.click();
    URL.revokeObjectURL(url);
  }, [filteredActors, stats, onExport]);

  return (
    <div className={`glass-card p-4 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-3">
          <h3 className="text-sm font-semibold text-white">🌐 NETWORK INTELLIGENCE</h3>
          <div className="flex items-center gap-2 text-xs">
            <span className="flex items-center gap-1 text-dark-muted">
              <Users className="w-3 h-3" />
              {stats.filtered}/{stats.total}
            </span>
            <span className="flex items-center gap-1 text-red-400">
              <AlertTriangle className="w-3 h-3" />
              {stats.highRisk}
            </span>
            <span className="flex items-center gap-1 text-yellow-400">
              <Shield className="w-3 h-3" />
              {stats.collusion}
            </span>
          </div>
        </div>
        <div className="flex items-center gap-3 text-xs">
          <span className="text-dark-muted">{filteredActors.length} Entities</span>
          <span className="text-dark-muted">
            {filteredActors.reduce((acc, a) => acc + (a.connections || 0), 0)} Relationships
          </span>
        </div>
      </div>

      {/* Filters */}
      <NetworkFilters
        onSearch={setSearchQuery}
        onFilterRisk={setRiskFilter}
        onFilterCommunity={setCommunityFilter}
        onExport={handleExport}
        onRefresh={handleRefresh}
        communities={communities}
        totalActors={actors.length}
        filteredActors={filteredActors.length}
        isLoading={isLoading}
      />

      {/* Graph */}
      <div style={{ height }} className="relative">
        {filteredActors.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-dark-muted">
            <div className="text-4xl mb-2">🔍</div>
            <p>Tidak ada data sesuai filter</p>
            <button
              onClick={resetFilters}
              className="mt-2 text-sm text-primary-400 hover:text-primary-300"
            >
              Reset filters
            </button>
          </div>
        ) : (
          <NetworkGraph
            actors={filteredActors}
            height={height}
            onNodeClick={onNodeClick}
          />
        )}
      </div>

      {/* Legend */}
      <div className="flex flex-wrap items-center gap-4 mt-3 pt-3 border-t border-dark-border text-xs">
        <span className="text-dark-muted font-medium">Legend:</span>
        <div className="flex items-center gap-2">
          <span className="w-3 h-3 rounded-full bg-red-500" />
          <span className="text-dark-muted">Critical Risk</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-3 h-3 rounded-full bg-orange-500" />
          <span className="text-dark-muted">High Risk</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-3 h-3 rounded-full bg-yellow-500" />
          <span className="text-dark-muted">Medium Risk</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-3 h-3 rounded-full bg-green-500" />
          <span className="text-dark-muted">Low Risk</span>
        </div>
        <div className="flex items-center gap-2 ml-auto">
          <span className="w-6 h-0.5 bg-red-400 border-t-2 border-red-400 border-dashed" />
          <span className="text-dark-muted">Collusion</span>
        </div>
      </div>
    </div>
  );
};

export default EnhancedNetworkGraph;
