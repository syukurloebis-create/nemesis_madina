// NetworkFilters.tsx - Filter panel untuk graph
import React, { useState } from 'react';
import { Search, Filter, X, Download, RefreshCw } from 'lucide-react';

interface NetworkFiltersProps {
  onSearch: (query: string) => void;
  onFilterRisk: (level: string) => void;
  onFilterCommunity: (community: string) => void;
  onExport: () => void;
  onRefresh: () => void;
  communities: string[];
  totalActors: number;
  filteredActors: number;
  isLoading?: boolean;
}

export const NetworkFilters: React.FC<NetworkFiltersProps> = ({
  onSearch,
  onFilterRisk,
  onFilterCommunity,
  onExport,
  onRefresh,
  communities,
  totalActors,
  filteredActors,
  isLoading = false
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [isFilterOpen, setIsFilterOpen] = useState(false);

  const handleSearch = (value: string) => {
    setSearchQuery(value);
    onSearch(value);
  };

  const riskOptions = [
    { value: 'ALL', label: 'All Risks' },
    { value: 'CRITICAL', label: 'Critical (80-100)', color: 'text-red-400' },
    { value: 'HIGH', label: 'High (60-79)', color: 'text-orange-400' },
    { value: 'MEDIUM', label: 'Medium (40-59)', color: 'text-yellow-400' },
    { value: 'LOW', label: 'Low (0-39)', color: 'text-green-400' },
  ];

  return (
    <div className="glass-effect rounded-lg p-3 mb-3">
      <div className="flex flex-wrap items-center gap-3">
        {/* Search */}
        <div className="flex-1 min-w-[180px]">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-dark-muted" />
            <input
              type="text"
              placeholder="Search entities..."
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              className="w-full bg-dark-bg/50 border border-dark-border rounded-lg pl-9 pr-3 py-2 text-sm text-white placeholder-dark-muted focus:outline-none focus:border-primary-500/50 transition-colors"
            />
            {searchQuery && (
              <button
                onClick={() => handleSearch('')}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-dark-muted hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>

        {/* Risk Filter */}
        <select
          onChange={(e) => onFilterRisk(e.target.value)}
          className="bg-dark-bg/50 border border-dark-border rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-primary-500/50 transition-colors cursor-pointer"
          defaultValue="ALL"
        >
          {riskOptions.map((opt) => (
            <option key={opt.value} value={opt.value} className={opt.color || ''}>
              {opt.label}
            </option>
          ))}
        </select>

        {/* Community Filter */}
        <select
          onChange={(e) => onFilterCommunity(e.target.value)}
          className="bg-dark-bg/50 border border-dark-border rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-primary-500/50 transition-colors cursor-pointer"
          defaultValue="ALL"
        >
          <option value="ALL">All Communities</option>
          {communities.map((c) => (
            <option key={c} value={c} className="capitalize">
              {c}
            </option>
          ))}
        </select>

        {/* Action Buttons */}
        <div className="flex items-center gap-2">
          <button
            onClick={onRefresh}
            disabled={isLoading}
            className="p-2 bg-dark-bg/50 border border-dark-border rounded-lg text-dark-muted hover:text-white hover:border-primary-500/30 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
          <button
            onClick={onExport}
            className="p-2 bg-dark-bg/50 border border-dark-border rounded-lg text-dark-muted hover:text-white hover:border-primary-500/30 transition-colors"
          >
            <Download className="w-4 h-4" />
          </button>
        </div>

        {/* Stats */}
        <div className="text-xs text-dark-muted ml-auto">
          {filteredActors} of {totalActors} actors
        </div>
      </div>

      {/* Active Filters */}
      {(searchQuery || communities.length > 0) && (
        <div className="flex flex-wrap items-center gap-2 mt-2 pt-2 border-t border-dark-border/30">
          <span className="text-xs text-dark-muted">Active filters:</span>
          {searchQuery && (
            <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-primary-500/20 text-primary-400 rounded-full text-xs">
              Search: {searchQuery}
              <button onClick={() => handleSearch('')} className="hover:text-white">
                <X className="w-3 h-3" />
              </button>
            </span>
          )}
          {communities.length > 0 && (
            <span className="text-xs text-dark-muted">{communities.length} communities</span>
          )}
        </div>
      )}
    </div>
  );
};

export default NetworkFilters;
