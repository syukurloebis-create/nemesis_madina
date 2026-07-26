// src/stores/entityStore.ts
import { create } from 'zustand';

export interface Entity {
  id: string;
  name: string;
  type: 'vendor' | 'institution' | 'individual' | 'package';
  risk_score: number;
  trust_score: number;
  total_cases: number;
  total_amount: number;
  first_seen: string;
  last_seen: string;
  metadata: Record<string, any>;
}

export interface Relationship {
  id: string;
  source: string;
  target: string;
  type: 'related' | 'collusion' | 'contract' | 'payment';
  strength: number;
  cases: string[];
}

export interface TrustPoint {
  timestamp: string;
  score: number;
  event: string;
  case_id: string;
}

interface EntityState {
  entities: Entity[];
  selectedEntity: Entity | null;
  relationships: Relationship[];
  trustHistory: TrustPoint[];
  loading: boolean;
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  selectEntity: (entity: Entity | null) => void;
  fetchEntities: () => Promise<void>;
  fetchEntityRelationships: (entityId: string) => Promise<void>;
  fetchTrustHistory: (entityId: string) => Promise<void>;
}

// Mock data for development
const mockEntities: Entity[] = [
  {
    id: 'VENDOR-001',
    name: 'PT. Maju Jaya Konstruksi',
    type: 'vendor',
    risk_score: 85,
    trust_score: 45,
    total_cases: 3,
    total_amount: 2500000000,
    first_seen: '2024-01-15',
    last_seen: '2026-06-01',
    metadata: { address: 'Jakarta', sector: 'Construction' }
  },
  {
    id: 'VENDOR-002',
    name: 'CV. Karya Mandiri',
    type: 'vendor',
    risk_score: 92,
    trust_score: 32,
    total_cases: 5,
    total_amount: 1800000000,
    first_seen: '2024-03-20',
    last_seen: '2026-05-28',
    metadata: { address: 'Bandung', sector: 'Consulting' }
  },
  {
    id: 'INST-001',
    name: 'Kementerian PUPR',
    type: 'institution',
    risk_score: 45,
    trust_score: 78,
    total_cases: 8,
    total_amount: 15000000000,
    first_seen: '2023-01-10',
    last_seen: '2026-06-07',
    metadata: { sector: 'Government' }
  },
];

const mockRelationships: Relationship[] = [
  { id: 'rel-1', source: 'VENDOR-001', target: 'VENDOR-002', type: 'collusion', strength: 0.85, cases: ['CASE-001', 'CASE-002'] },
  { id: 'rel-2', source: 'VENDOR-001', target: 'INST-001', type: 'contract', strength: 0.92, cases: ['CASE-001'] },
];

const mockTrustHistory: TrustPoint[] = [
  { timestamp: '2025-01-01', score: 75, event: 'Initial registration', case_id: '' },
  { timestamp: '2025-04-01', score: 68, event: 'First contract signed', case_id: 'CASE-001' },
  { timestamp: '2025-07-01', score: 55, event: 'Payment delay detected', case_id: 'CASE-002' },
  { timestamp: '2026-01-01', score: 42, event: 'Investigation started', case_id: 'CASE-004' },
  { timestamp: '2026-06-01', score: 32, event: 'Collusion detected', case_id: 'CASE-005' },
];

export const useEntityStore = create<EntityState>((set, get) => ({
  entities: mockEntities,
  selectedEntity: null,
  relationships: [],
  trustHistory: [],
  loading: false,
  searchQuery: '',

  setSearchQuery: (query) => set({ searchQuery: query }),
  
  selectEntity: (entity) => set({ selectedEntity: entity }),
  
  fetchEntities: async () => {
    set({ loading: true });
    setTimeout(() => {
      set({ entities: mockEntities, loading: false });
    }, 500);
  },
  
  fetchEntityRelationships: async (entityId) => {
    set({ loading: true });
    setTimeout(() => {
      const filtered = mockRelationships.filter(
        r => r.source === entityId || r.target === entityId
      );
      set({ relationships: filtered, loading: false });
    }, 500);
  },
  
  fetchTrustHistory: async (entityId) => {
    set({ loading: true });
    setTimeout(() => {
      set({ trustHistory: mockTrustHistory, loading: false });
    }, 500);
  },
}));
