/**
 * NEMESIS V8+ - Decision System Types
 */

export interface Decision {
  id: string;
  caseId: string;
  title: string;
  description: string;
  type: 'RECOMMENDATION' | 'ACTION' | 'APPROVAL' | 'ESCALATION';
  status: 'PENDING' | 'APPROVED' | 'REJECTED' | 'IMPLEMENTED' | 'ESCALATED' | 'IN_REVIEW';
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  confidence: number;
  createdAt: Date;
  updatedAt: Date;
  createdBy: string;
  createdByName: string;
  assignedTo?: string;
  assignedToName?: string;
  dueDate?: Date;
  approvedAt?: Date;
  approvedBy?: string;
  approvedByName?: string;
  rejectionReason?: string;
  implementationNotes?: string;
  evidence: DecisionEvidence[];
  votes: DecisionVote[];
  comments: DecisionComment[];
  tags: string[];
  actions: DecisionAction[];
}

export interface DecisionEvidence {
  id: string;
  type: 'DOCUMENT' | 'TRANSACTION' | 'RELATIONSHIP' | 'PATTERN' | 'STATEMENT';
  title: string;
  description: string;
  confidence: number;
  source: string;
  url?: string;
  referenceId?: string;
}

export interface DecisionVote {
  userId: string;
  userName: string;
  vote: 'APPROVE' | 'REJECT' | 'ABSTAIN' | 'ESCALATE';
  comment?: string;
  timestamp: Date;
}

export interface DecisionComment {
  id: string;
  userId: string;
  userName: string;
  content: string;
  timestamp: Date;
  parentId?: string;
}

export interface DecisionAction {
  id: string;
  type: 'INVESTIGATE' | 'REVIEW' | 'ESCALATE' | 'IMPLEMENT' | 'REJECT' | 'APPROVE';
  label: string;
  description: string;
  priority: number;
  handler: (decision: Decision) => Promise<void>;
  isEnabled: boolean;
  isVisible: boolean;
}

export interface DecisionFilter {
  status?: Decision['status'][];
  priority?: Decision['priority'][];
  type?: Decision['type'][];
  search?: string;
  assignedTo?: string;
  fromDate?: Date;
  toDate?: Date;
}

export interface DecisionStats {
  total: number;
  pending: number;
  approved: number;
  rejected: number;
  implemented: number;
  escalated: number;
  byPriority: {
    LOW: number;
    MEDIUM: number;
    HIGH: number;
    CRITICAL: number;
  };
  byType: {
    RECOMMENDATION: number;
    ACTION: number;
    APPROVAL: number;
    ESCALATION: number;
  };
  averageApprovalTime: number; // in hours
  approvalRate: number; // percentage
}

export interface DecisionTrace {
 id:string;
 decisionId:string;
 action:string;
 timestamp:Date;
 user?:string;
 metadata?:Record<string,any>;
}

export interface DecisionTrace {
  id: string;
  decisionId: string;
  action: string;
  timestamp: Date;
  actor?: string;
  metadata?: Record<string, any>;
}
