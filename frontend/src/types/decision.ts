export interface IDecision {
  id: string;
  caseId: string;
  type: 'RECOMMENDATION' | 'ACTION' | 'APPROVAL' | 'ESCALATION';
  title: string;
  description: string;
  impact: 'HIGH' | 'MEDIUM' | 'LOW';
  confidence: number;
  status: 'PENDING' | 'APPROVED' | 'REJECTED' | 'IMPLEMENTED' | 'ESCALATED';
  createdAt: Date;
  updatedAt: Date;
  createdBy: string;
  evidence: IDecisionEvidence[];
  explanation: string;
  votes: IDecisionVote[];
  comments: IDecisionComment[];
  tags: string[];
}

export interface IDecisionEvidence {
  id: string;
  type: string;
  title: string;
  description: string;
  confidence: number;
  source: string;
  url?: string;
}

export interface IDecisionVote {
  userId: string;
  userName: string;
  vote: 'APPROVE' | 'REJECT' | 'ABSTAIN';
  comment?: string;
  timestamp: Date;
}

export interface IDecisionComment {
  id: string;
  userId: string;
  userName: string;
  content: string;
  timestamp: Date;
}

export interface IDecisionConfig {
  minApprovals: number;
  maxRejections: number;
  requiredRoles: string[];
  escalationThreshold: number;
  autoApprovalConfidence: number;
}
