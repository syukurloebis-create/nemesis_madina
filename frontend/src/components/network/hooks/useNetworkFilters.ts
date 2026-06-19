// useNetworkFilters.ts - Hook untuk filter logic
import { useState, useMemo, useCallback } from 'react';

interface Actor {
  id?: string;
  name: string;
  risk_score: number;
  connections?: number;
  connection_type?: string;
  community?: string;
}

interface UseNetworkFiltersReturn {
  searchQuery: string;
  riskFilter: string;
  communityFilter: string;
  filteredActors: Actor[];
  communities: string[];
  setSearchQuery: (query: string) => void;
  setRiskFilter: (level: string) => void;
  setCommunityFilter: (community: string) => void;
  resetFilters: () => void;
}

export const useNetworkFilters = (actors: Actor[]): UseNetworkFiltersReturn => {
  const [searchQuery, setSearchQuery] = useState('');
  const [riskFilter, setRiskFilter] = useState('ALL');
  const [communityFilter, setCommunityFilter] = useState('ALL');

  // Get unique communities
  const communities = useMemo(() => {
    const comms = new Set(actors.map(a => a.community || 'unclassified'));
    return Array.from(comms);
  }, [actors]);

  // Filter actors
  const filteredActors = useMemo(() => {
    return actors.filter(actor => {
      // Search filter
      if (searchQuery && !actor.name.toLowerCase().includes(searchQuery.toLowerCase())) {
        return false;
      }
      
      // Risk filter
      if (riskFilter !== 'ALL') {
        const score = actor.risk_score || 0;
        if (riskFilter === 'CRITICAL' && score < 80) return false;
        if (riskFilter === 'HIGH' && (score < 60 || score >= 80)) return false;
        if (riskFilter === 'MEDIUM' && (score < 40 || score >= 60)) return false;
        if (riskFilter === 'LOW' && score >= 40) return false;
      }
      
      // Community filter
      if (communityFilter !== 'ALL' && actor.community !== communityFilter) {
        return false;
      }
      
      return true;
    });
  }, [actors, searchQuery, riskFilter, communityFilter]);

  const resetFilters = useCallback(() => {
    setSearchQuery('');
    setRiskFilter('ALL');
    setCommunityFilter('ALL');
  }, []);

  return {
    searchQuery,
    riskFilter,
    communityFilter,
    filteredActors,
    communities,
    setSearchQuery,
    setRiskFilter,
    setCommunityFilter,
    resetFilters
  };
};

export default useNetworkFilters;
