// types/evidence.ts - Evidence Chain of Custody Types

export type EvidenceStatus = 'UPLOADED' | 'VERIFIED' | 'REJECTED' | 'PENDING' | 'IN_REVIEW';
export type CustodyAction = 'UPLOAD' | 'VERIFY' | 'REJECT' | 'REVIEW' | 'TRANSFER' | 'ARCHIVE';

export interface CustodyEvent {
  id: string;
  evidence_id: string;
  action: CustodyAction;
  actor: string;
  timestamp: string;
  notes?: string;
  metadata?: Record<string, any>;
}

export interface Evidence {
  id: string;
  case_id: string;
  filename: string;
  file_type: string;
  file_size: number;
  file_hash: string;
  trust_score: number;
  status: EvidenceStatus;
  verified_at?: string;
  uploaded_at: string;
  updated_at: string;
  scoring_detail?: Record<string, any>;
  confidence_level?: string;
  custody_events?: CustodyEvent[];
  case_title?: string;
}

export interface EvidenceChain {
  evidence: Evidence;
  custody_events: CustodyEvent[];
  timeline: {
    date: string;
    events: CustodyEvent[];
  }[];
  summary: {
    total_events: number;
    unique_actors: string[];
    actions: Record<CustodyAction, number>;
    chain_integrity: number;
  };
}

export interface EvidenceStats {
  total: number;
  verified: number;
  pending: number;
  rejected: number;
  by_case: Record<string, number>;
  average_trust: number;
}

export interface EvidenceChainProps {
  evidenceId: string;
  className?: string;
  onVerify?: (id: string) => void;
  onReject?: (id: string) => void;
}
