/**
 * NEMESIS V8+ - Dashboard Data Types
 * Single Source of Truth untuk semua data dashboard
 */

export interface DashboardData {
  // Executive Overview
  executive: ExecutiveData;
  
  // Cases
  cases: CaseData[];
  
  // Evidence
  evidence: EvidenceData;
  
  // Graph Intelligence
  graph: GraphData;
  
  // Fraud Detection
  fraud: FraudData;
  
  // RUP (Procurement)
  rup: RUPData;
  
  // Statistics
  stats: StatsData;
  
  // Risk
  risk: RiskData;
  
  // Recommendations
  recommendations: RecommendationData[];
  
  // System Status
  systemStatus: SystemStatus;
}

export interface ExecutiveData {
  totalCases: number;
  activeCases: number;
  highRiskCases: number;
  criticalAlerts: number;
  avgResolutionTime: number;
  riskScore: number;
}

export interface CaseData {
  id: string;
  title: string;
  status: 'ACTIVE' | 'CLOSED' | 'PENDING' | 'ESCALATED';
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  riskScore: number;
  createdAt: Date;
  updatedAt: Date;
  assignedTo?: string;
  description?: string;
  evidenceCount: number;
}

export interface EvidenceData {
  total: number;
  verified: number;
  pending: number;
  rejected: number;
  recent: EvidenceItem[];
  categories: {
    [key: string]: number;
  };
}

export interface EvidenceItem {
  id: string;
  title: string;
  type: string;
  status: 'PENDING' | 'VERIFIED' | 'REJECTED';
  confidence: number;
  createdAt: Date;
  source: string;
}

export interface GraphData {
  entities: GraphEntity[];
  relationships: GraphRelationship[];
  metrics: GraphMetrics;
  keyActors: KeyActor[];
  communities: Community[];
  clusters: Cluster[];
}

export interface GraphEntity {
  id: string;
  name: string;
  type: string;
  riskScore: number;
  confidence: number;
  connections: number;
  attributes: Record<string, any>;
}

export interface GraphRelationship {
  id: string;
  sourceId: string;
  targetId: string;
  type: string;
  weight: number;
  attributes: Record<string, any>;
}

export interface GraphMetrics {
  nodes: number;
  edges: number;
  density: number;
  modularity: number;
  avgDegree: number;
  diameter: number;
}

export interface KeyActor {
  id: string;
  name: string;
  type: string;
  influence: number;
  centrality: number;
  connections: number;
  riskScore: number;
  role: string;
}

export interface Community {
  id: string;
  name?: string;
  members: string[];
  size: number;
  density: number;
  riskScore: number;
  riskLevel: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
}

export interface Cluster {
  id: string;
  name?: string;
  members: string[];
  size: number;
  riskScore: number;
}

export interface FraudData {
  patterns: FraudPattern[];
  indicators: FraudIndicator[];
  signals: FraudSignal[];
  confidence: number;
  riskScore: number;
  alerts: FraudAlert[];
}

export interface FraudPattern {
  id: string;
  type: string;
  description: string;
  confidence: number;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  entities: string[];
  timestamp: Date;
}

export interface FraudIndicator {
  id: string;
  type: string;
  description: string;
  weight: number;
  score: number;
  triggered: boolean;
}

export interface FraudSignal {
  id: string;
  type: string;
  source: string;
  confidence: number;
  details: Record<string, any>;
  timestamp: Date;
}

export interface FraudAlert {
  id: string;
  type: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  title: string;
  description: string;
  timestamp: Date;
  status: 'NEW' | 'ACKNOWLEDGED' | 'RESOLVED';
}

export interface RUPData {
  totalPackages: number;
  totalValue: number;
  byCategory: {
    [key: string]: {
      count: number;
      value: number;
    };
  };
  recent: RUPPackage[];
  highRiskVendors: string[];
}

export interface RUPPackage {
  id: string;
  title: string;
  vendor: string;
  value: number;
  status: 'DRAFT' | 'PUBLISHED' | 'AWARDED' | 'COMPLETED';
  riskScore: number;
  createdAt: Date;
}

export interface StatsData {
  totalCases: number;
  activeCases: number;
  resolvedCases: number;
  avgRiskScore: number;
  totalEvidence: number;
  totalEntities: number;
  totalRelationships: number;
  fraudDetections: number;
}

export interface RiskData {
  score: number;
  level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  factors: RiskFactor[];
  trend: 'DECREASING' | 'STABLE' | 'INCREASING';
  historical: HistoricalRisk[];
}

export interface RiskFactor {
  id: string;
  category: string;
  description: string;
  score: number;
  weight: number;
  confidence: number;
}

export interface HistoricalRisk {
  date: Date;
  score: number;
  level: string;
  event: string;
}

export interface RecommendationData {
  id: string;
  type: 'PREVENTIVE' | 'DETECTIVE' | 'CORRECTIVE';
  title: string;
  description: string;
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  confidence: number;
  impact: number;
  effort: number;
  actions: string[];
  status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'REJECTED';
}

export interface SystemStatus {
  isOnline: boolean;
  lastUpdate: Date;
  services: {
    api: boolean;
    database: boolean;
    graphEngine: boolean;
    aiEngine: boolean;
  };
  metrics: {
    responseTime: number;
    uptime: number;
    memoryUsage: number;
  };
}
