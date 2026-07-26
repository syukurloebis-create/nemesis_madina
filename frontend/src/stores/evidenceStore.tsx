// src/stores/evidenceStore.ts
import { create } from 'zustand';

interface Evidence {
    id: string;
    case_id: string;
    filename: string;
    sha256_hash: string;
    file_size: number;
    uploaded_by: string;
    uploaded_at: string;
    verification_status?: string;
}

interface EvidenceState {
    evidence: Evidence[];
    currentEvidence: Evidence | null;
    custodyHistory: any[];
    isLoading: boolean;
    setEvidence: (evidence: Evidence[]) => void;
    setCurrentEvidence: (evidence: Evidence | null) => void;
    setCustodyHistory: (history: any[]) => void;
    setLoading: (loading: boolean) => void;
}

export const useEvidenceStore = create<EvidenceState>((set) => ({
    evidence: [],
    currentEvidence: null,
    custodyHistory: [],
    isLoading: false,
    setEvidence: (evidence) => set({ evidence }),
    setCurrentEvidence: (currentEvidence) => set({ currentEvidence }),
    setCustodyHistory: (custodyHistory) => set({ custodyHistory }),
    setLoading: (isLoading) => set({ isLoading }),
}));