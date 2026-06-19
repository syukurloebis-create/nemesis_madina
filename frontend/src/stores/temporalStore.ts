// src/stores/temporalStore.ts
import { create } from 'zustand';

export interface TimelineEvent {
  id: string;
  case_id: string;
  case_title: string;
  event_type: string;
  event_data: Record<string, any>;
  timestamp: string;
  user: string;
  hash: string;
  previous_hash: string;
}

export interface ReplayState {
  isPlaying: boolean;
  currentIndex: number;
  speed: number;
  events: TimelineEvent[];
  filteredEvents: TimelineEvent[];
  selectedEvent: TimelineEvent | null;
  filters: {
    case_id: string;
    event_type: string;
    date_from: string;
    date_to: string;
  };
  loading: boolean;
  
  setPlaying: (isPlaying: boolean) => void;
  setCurrentIndex: (index: number) => void;
  setSpeed: (speed: number) => void;
  setSelectedEvent: (event: TimelineEvent | null) => void;
  setFilters: (filters: any) => void;
  fetchEvents: () => Promise<void>;
  nextEvent: () => void;
  prevEvent: () => void;
}

// Mock events data
const mockEvents: TimelineEvent[] = [
  {
    id: 'evt-001',
    case_id: 'CASE-001',
    case_title: 'Procurement Investigation',
    event_type: 'case_created',
    event_data: { title: 'Procurement Investigation', priority: 'HIGH' },
    timestamp: '2026-06-01T09:00:00Z',
    user: 'auditor@inspektorat.go.id',
    hash: '0x7d4e...',
    previous_hash: ''
  },
  {
    id: 'evt-002',
    case_id: 'CASE-001',
    case_title: 'Procurement Investigation',
    event_type: 'evidence_added',
    event_data: { evidence_id: 'EVID-001', type: 'document' },
    timestamp: '2026-06-01T10:30:00Z',
    user: 'investigator@kpk.go.id',
    hash: '0x8e5f...',
    previous_hash: '0x7d4e...'
  },
  {
    id: 'evt-003',
    case_id: 'CASE-001',
    case_title: 'Procurement Investigation',
    event_type: 'risk_score_updated',
    event_data: { old_score: 45, new_score: 68 },
    timestamp: '2026-06-02T14:20:00Z',
    user: 'system',
    hash: '0x9g6h...',
    previous_hash: '0x8e5f...'
  },
  {
    id: 'evt-004',
    case_id: 'CASE-002',
    case_title: 'Vendor Collusion',
    event_type: 'case_created',
    event_data: { title: 'Vendor Collusion', priority: 'CRITICAL' },
    timestamp: '2026-06-03T08:15:00Z',
    user: 'auditor@bpkp.go.id',
    hash: '0x1a2b...',
    previous_hash: ''
  },
  {
    id: 'evt-005',
    case_id: 'CASE-002',
    case_title: 'Vendor Collusion',
    event_type: 'relationship_detected',
    event_data: { source: 'VENDOR-001', target: 'VENDOR-002', type: 'collusion' },
    timestamp: '2026-06-04T11:45:00Z',
    user: 'system',
    hash: '0x2c3d...',
    previous_hash: '0x1a2b...'
  },
  {
    id: 'evt-006',
    case_id: 'CASE-001',
    case_title: 'Procurement Investigation',
    event_type: 'status_changed',
    event_data: { old_status: 'OPEN', new_status: 'INVESTIGATING' },
    timestamp: '2026-06-05T09:30:00Z',
    user: 'investigator@kpk.go.id',
    hash: '0x3e4f...',
    previous_hash: '0x9g6h...'
  },
  {
    id: 'evt-007',
    case_id: 'CASE-002',
    case_title: 'Vendor Collusion',
    event_type: 'anomaly_detected',
    event_data: { anomaly_type: 'collusion', confidence: 0.92 },
    timestamp: '2026-06-06T13:00:00Z',
    user: 'system',
    hash: '0x4f5g...',
    previous_hash: '0x2c3d...'
  },
  {
    id: 'evt-008',
    case_id: 'CASE-001',
    case_title: 'Procurement Investigation',
    event_type: 'case_resolved',
    event_data: { resolution: 'Refer to legal' },
    timestamp: '2026-06-07T10:00:00Z',
    user: 'auditor@inspektorat.go.id',
    hash: '0x5g6h...',
    previous_hash: '0x3e4f...'
  }
];

export const useTemporalStore = create<ReplayState>((set, get) => ({
  events: mockEvents,
  filteredEvents: mockEvents,
  selectedEvent: null,
  isPlaying: false,
  currentIndex: 0,
  speed: 1,
  filters: {
    case_id: '',
    event_type: '',
    date_from: '',
    date_to: ''
  },
  loading: false,

  setPlaying: (isPlaying) => set({ isPlaying }),
  
  setCurrentIndex: (currentIndex) => set({ currentIndex }),
  
  setSpeed: (speed) => set({ speed }),
  
  setSelectedEvent: (selectedEvent) => set({ selectedEvent }),
  
  setFilters: (filters) => {
    set({ filters });
    const { events, filters: f } = get();
    const filtered = events.filter(event => {
      if (f.case_id && !event.case_id.includes(f.case_id)) return false;
      if (f.event_type && event.event_type !== f.event_type) return false;
      if (f.date_from && new Date(event.timestamp) < new Date(f.date_from)) return false;
      if (f.date_to && new Date(event.timestamp) > new Date(f.date_to)) return false;
      return true;
    });
    set({ filteredEvents: filtered, currentIndex: 0 });
  },
  
  fetchEvents: async () => {
    set({ loading: true });
    // Simulate API call
    setTimeout(() => {
      set({ events: mockEvents, filteredEvents: mockEvents, loading: false });
    }, 500);
  },
  
  nextEvent: () => {
    const { currentIndex, filteredEvents } = get();
    if (currentIndex < filteredEvents.length - 1) {
      set({ currentIndex: currentIndex + 1, selectedEvent: filteredEvents[currentIndex + 1] });
    }
  },
  
  prevEvent: () => {
    const { currentIndex, filteredEvents } = get();
    if (currentIndex > 0) {
      set({ currentIndex: currentIndex - 1, selectedEvent: filteredEvents[currentIndex - 1] });
    }
  }
}));
