// types/decision.ts - Decision Support Types

export type DecisionPriority = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
export type DecisionStatus = 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'REJECTED' | 'CANCELLED';
export type DecisionAction = 'AUDIT_INVESTIGATIF' | 'KLARIFIKASI' | 'MONITORING' | 'ADMINISTRATIF' | 'TINDAK_LANJUT';

export interface DecisionEvidence {
  id: string;
  title: string;
  type: string;
  trust_score: number;
  status: string;
  link?: string;
}

export interface DecisionJustification {
  id: string;
  factor: string;
  description: string;
  weight: number;
  contribution: number;
  evidence: DecisionEvidence[];
}

export interface Decision {
  id: string;
  case_id: string;
  case_title: string;
  title: string;
  description: string;
  priority: DecisionPriority;
  action: DecisionAction;
  justification: DecisionJustification[];
  evidence: DecisionEvidence[];
  status: DecisionStatus;
  assigned_to?: string;
  created_at: string;
  due_date: string;
  completed_at?: string;
  notes?: string;
}

export interface DecisionSummary {
  total: number;
  by_priority: Record<DecisionPriority, number>;
  by_status: Record<DecisionStatus, number>;
  by_action: Record<DecisionAction, number>;
}

export interface DecisionSupportProps {
  caseId?: string;
  className?: string;
  onActionClick?: (decision: Decision) => void;
  onStatusChange?: (decisionId: string, status: DecisionStatus) => void;
}
