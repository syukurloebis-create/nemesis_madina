// src/hooks/useNetworkFilters.ts
import { useState, useMemo, useCallback } from 'react';

// ============ FIX: Export NetworkNode ============
export interface NetworkNode {
  id: string;
  name: string;
  type?: string;
  risk_score?: number;
  connections?: number;
  [key: string]: any;
}

export interface NetworkFilters {
  search: string;
  minRisk: number;
  maxRisk: number;
  types: string[];
  minConnections: number;
}

export interface UseNetworkFiltersReturn {
  filters: NetworkFilters;
  setSearch: (search: string) => void;
  setMinRisk: (minRisk: number) => void;
  setMaxRisk: (maxRisk: number) => void;
  setTypes: (types: string[]) => void;
  setMinConnections: (minConnections: number) => void;
  resetFilters: () => void;
  filteredData: NetworkNode[];
  availableTypes: string[];
}

const defaultFilters: NetworkFilters = {
  search: '',
  minRisk: 0,
  maxRisk: 100,
  types: [],
  minConnections: 0,
};

export const useNetworkFilters = (
  data: NetworkNode[] = [],
  options: { initialFilters?: Partial<NetworkFilters> } = {}
): UseNetworkFiltersReturn => {
  const [filters, setFilters] = useState<NetworkFilters>({
    ...defaultFilters,
    ...options.initialFilters,
  });

  const setSearch = useCallback((search: string) => {
    setFilters(prev => ({ ...prev, search }));
  }, []);

  const setMinRisk = useCallback((minRisk: number) => {
    setFilters(prev => ({ ...prev, minRisk }));
  }, []);

  const setMaxRisk = useCallback((maxRisk: number) => {
    setFilters(prev => ({ ...prev, maxRisk }));
  }, []);

  const setTypes = useCallback((types: string[]) => {
    setFilters(prev => ({ ...prev, types }));
  }, []);

  const setMinConnections = useCallback((minConnections: number) => {
    setFilters(prev => ({ ...prev, minConnections }));
  }, []);

  const resetFilters = useCallback(() => {
    setFilters(defaultFilters);
  }, []);

  const availableTypes = useMemo(() => {
    if (!data || !Array.isArray(data) || data.length === 0) {
      return [];
    }
    const types = new Set<string>();
    data.forEach((item: NetworkNode) => {
      if (item.type) {
        types.add(item.type);
      }
    });
    return Array.from(types);
  }, [data]);

  const filteredData = useMemo(() => {
    if (!data || !Array.isArray(data) || data.length === 0) {
      return [];
    }

    return data.filter((item: NetworkNode) => {
      if (filters.search) {
        const searchLower = filters.search.toLowerCase();
        const nameMatch = item.name?.toLowerCase().includes(searchLower) || false;
        const idMatch = item.id?.toLowerCase().includes(searchLower) || false;
        if (!nameMatch && !idMatch) return false;
      }

      const risk = item.risk_score ?? 0;
      if (risk < filters.minRisk || risk > filters.maxRisk) return false;

      if (filters.types.length > 0) {
        if (!item.type || !filters.types.includes(item.type)) return false;
      }

      const connections = item.connections ?? 0;
      if (connections < filters.minConnections) return false;

      return true;
    });
  }, [data, filters]);

  return {
    filters,
    setSearch,
    setMinRisk,
    setMaxRisk,
    setTypes,
    setMinConnections,
    resetFilters,
    filteredData,
    availableTypes,
  };
};

export default useNetworkFilters;
