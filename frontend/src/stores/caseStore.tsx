import { create } from 'zustand';
import { casesApi } from '../services/api';

interface CaseState {
  cases: any[];
  selectedCase: any | null;
  loading: boolean;
  error: string | null;
  fetchCases: () => Promise<void>;
  selectCase: (id: string) => Promise<void>;
}

export const useCaseStore = create<CaseState>((set) => ({
  cases: [],
  selectedCase: null,
  loading: false,
  error: null,
  fetchCases: async () => {
    set({ loading: true, error: null });
    try {
      const response = await casesApi.getCases();
      const data = response?.data || response || [];
      set({ cases: Array.isArray(data) ? data : [], loading: false });
    } catch (error) {
      set({ loading: false, error: 'Failed to fetch cases' });
    }
  },
  selectCase: async (id: string) => {
    try {
      const response = await casesApi.getCase(id);
      set({ selectedCase: response?.data || response });
    } catch {
      // handle error
    }
  },
}));
