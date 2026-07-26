// src/stores/integrityStore.ts - New store
import { create } from 'zustand';

interface IntegrityResult {
    status: string;
    events_verified: number;
    chain_intact: boolean;
    failed_events: any[];
}

interface IntegrityState {
    results: Map<string, IntegrityResult>;
    overallStatus: string | null;
    isLoading: boolean;
    setResult: (caseId: string, result: IntegrityResult) => void;
    setOverallStatus: (status: string) => void;
    setLoading: (loading: boolean) => void;
}

export const useIntegrityStore = create<IntegrityState>((set) => ({
    results: new Map(),
    overallStatus: null,
    isLoading: false,
    setResult: (caseId, result) => set((state) => ({ 
        results: new Map(state.results).set(caseId, result) 
    })),
    setOverallStatus: (overallStatus) => set({ overallStatus }),
    setLoading: (isLoading) => set({ isLoading }),
}));