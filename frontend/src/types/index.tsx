// ============================================
// NEMESIS V8+ - MASTER TYPES
// ============================================

// FRAUD TYPES
export type FraudSeverity = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
export type FraudTrend = 'RISING' | 'STABLE' | 'DECLINING';
export type FraudStatus = 'ACTIVE' | 'INVESTIGATING' | 'RESOLVED' | 'FALSE_POSITIVE';

export interface FraudIndicator {
  id: string;
  name: string;
  description: string;
  weight: number;
  detected: boolean;
  confidence: number;
}

export interface FraudPattern {
  id: string;
  name: string;
  description: string;
  category: string;
  severity: FraudSeverity;
  confidence: number;
  trend: FraudTrend;
  status: FraudStatus;
  indicators: FraudIndicator[];
  cases: string[];
  affected_entities: string[];
  detected_at: string;
  updated_at: string;
  evidence_count: number;
}

export interface FraudPatternSummary {
  total: number;
  by_severity: Record<FraudSeverity, number>;
  by_status: Record<FraudStatus, number>;
  by_category: Record<string, number>;
  active_alerts: number;
  high_confidence: number;
}

// EVIDENCE TYPES
export interface Evidence {
  id: string;
  caseId: string;
  title: string;
  description?: string;
  fileType: string;
  fileSize: number;
  fileHash: string;
  status: 'UPLOADED' | 'VERIFIED' | 'REJECTED' | 'PENDING';
  trustScore: number;
  confidence: number;
  createdAt: string;
  updatedAt: string;
  uploadedBy: string;
  verifiedBy?: string;
  metadata?: Record<string, any>;
}

export interface CustodyRecord {
  id: string;
  evidenceId: string;
  from: string;
  to: string;
  action: 'TRANSFER' | 'VERIFY' | 'ANALYZE' | 'STORED';
  timestamp: string;
  actor: string;
  notes?: string;
}

export interface EvidenceStats {
  total: number;
  verified: number;
  pending: number;
  rejected: number;
  avgTrustScore: number;
}

// DECISION TYPES
export interface Decision {
  id: string;
  caseId: string;
  type: 'RISK_ASSESSMENT' | 'FRAUD_DETECTION' | 'EVIDENCE_EVALUATION' | 'RECOMMENDATION';
  title: string;
  description: string;
  reasoning: string;
  confidence: number;
  status: 'PENDING' | 'APPROVED' | 'REJECTED' | 'IMPLEMENTED';
  createdAt: string;
  updatedAt: string;
  createdBy: string;
  approvedBy?: string;
  metadata?: Record<string, any>;
}

export interface DecisionTrace {
  id: string;
  decisionId: string;
  step: number;
  action: string;
  actor: string;
  timestamp: string;
  details: Record<string, any>;
}

// PROVENANCE TYPES
export interface ProvenanceRecord {
  id: string;
  caseId: string;
  entityId: string;
  entityType: string;
  action: string;
  timestamp: string;
  actor: string;
  previousState?: Record<string, any>;
  newState?: Record<string, any>;
  metadata?: Record<string, any>;
}

export interface LineageNode {
  id: string;
  type: string;
  label: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

export interface LineageEdge {
  id: string;
  source: string;
  target: string;
  type: string;
  timestamp: string;
}

export interface ProvenanceGraph {
  nodes: LineageNode[];
  edges: LineageEdge[];
}

// INTELLIGENCE TYPES
export interface IntelligenceComponents {
  case_risk: number;
  graph_risk: number;
  fraud_score: number;
  evidence_trust: number;
}

export interface IntelligenceData {
  case_id: string;
  risk_score: number;
  risk_level: 'HIGH' | 'MEDIUM' | 'LOW';
  components: IntelligenceComponents;
  timestamp: string;
  version: string;
}

export interface GraphRiskData {
  graph_risk: number;
  level: string;
  entities: number;
  edges: number;
  confidence: number;
  data_source: string;
}

// EXPORT DEFAULT UNTUK KEMUDAHAN
export default {
  FraudSeverity: ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'] as FraudSeverity[],
  FraudStatus: ['ACTIVE', 'INVESTIGATING', 'RESOLVED', 'FALSE_POSITIVE'] as FraudStatus[],
  FraudTrend: ['RISING', 'STABLE', 'DECLINING'] as FraudTrend[],
};
