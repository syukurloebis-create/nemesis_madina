import { create } from 'zustand';
import { getCases, getCase, createCase, updateCase } from '../services/api';

interface Case {
  id: string;
  title: string;
  description: string;
  status: string;
  priority: string;
  created_at: string;
}

interface CaseStore {
  cases: Case[];
  selectedCase: Case | null;
  loading: boolean;
  error: string | null;
  fetchCases: () => Promise<void>;
  fetchCase: (id: string) => Promise<void>;
  addCase: (data: Partial<Case>) => Promise<void>;
  updateCase: (id: string, data: Partial<Case>) => Promise<void>;
}

export const useCaseStore = create<CaseStore>((set, get) => ({
  cases: [],
  selectedCase: null,
  loading: false,
  error: null,

  fetchCases: async () => {
    set({ loading: true, error: null });
    try {
      const response = await getCases();
      set({ cases: response.data, loading: false });
    } catch (error: any) {
      set({ error: error.message, loading: false });
    }
  },

  fetchCase: async (id: string) => {
    set({ loading: true, error: null });
    try {
      const response = await getCase(id);
      set({ selectedCase: response.data, loading: false });
    } catch (error: any) {
      set({ error: error.message, loading: false });
    }
  },

  addCase: async (data: Partial<Case>) => {
    set({ loading: true, error: null });
    try {
      const response = await createCase(data);
      const newCase = response.data;
      set({ cases: [newCase, ...get().cases], loading: false });
    } catch (error: any) {
      set({ error: error.message, loading: false });
    }
  },

  updateCase: async (id: string, data: Partial<Case>) => {
    set({ loading: true, error: null });
    try {
      const response = await updateCase(id, data);
      const updatedCase = response.data;
      set({
        cases: get().cases.map(c => c.id === id ? updatedCase : c),
        selectedCase: updatedCase,
        loading: false
      });
    } catch (error: any) {
      set({ error: error.message, loading: false });
    }
  },
}));
