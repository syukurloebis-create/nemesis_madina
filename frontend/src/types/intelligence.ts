export interface IUnifiedIntelligence {
  caseId: string;
  timestamp: Date;
  version: string;
  graph: any;
  risk: any;
  fraud: any;
  reasoning: any;
  metrics: any;
}

export interface IKeyActor {
  id: string;
  name: string;
  type: string;
  influence: number;
  centrality: number;
  connections: number;
  riskScore: number;
  collusionRisk: number;
  role: string;
  attributes: Record<string, any>;
}

export interface ICommunity {
  id: string;
  name?: string;
  members: string[];
  size: number;
  density: number;
  riskScore: number;
  riskLevel: string;
  suspiciousness: number;
}

export interface ICluster {
  id: string;
  name?: string;
  members: string[];
  size: number;
}

export interface IGraphMetrics {
  nodes: number;
  edges: number;
  density: number;
  modularity: number;
  avgDegree: number;
  diameter: number;
}

export interface IRiskFactor {
  id: string;
  category: string;
  description: string;
  weight: number;
  score: number;
  evidence: string[];
  confidence: number;
}

export interface IHistoricalRisk {
  date: Date;
  score: number;
  level: string;
  event: string;
}

export interface IFraudPattern {
  id: string;
  type: string;
  description: string;
  confidence: number;
  severity: string;
  entities: string[];
  evidence: string[];
  timestamp: Date;
}

export interface IFraudIndicator {
  id: string;
  type: string;
  description: string;
  weight: number;
  score: number;
  threshold: number;
  triggered: boolean;
}

export interface IFraudSignal {
  id: string;
  type: string;
  source: string;
  timestamp: Date;
  details: Record<string, any>;
  confidence: number;
}

export interface IRedFlag {
  id: string;
  type: string;
  description: string;
  severity: string;
  triggered: boolean;
  timestamp: Date;
  actionRequired: string;
}

export interface IReasoningRule {
  id: string;
  name: string;
  description: string;
  condition: string;
  priority: number;
  weight: number;
  triggered: boolean;
  confidence: number;
}

export interface IReasoningTrace {
  step: number;
  rule: string;
  input: any;
  output: any;
  confidence: number;
  timestamp: Date;
}

export interface IRecommendation {
  id: string;
  type: string;
  title: string;
  description: string;
  priority: string;
  confidence: number;
  impact: number;
  effort: number;
  roi: number;
  actions: string[];
  timeline: string;
  responsible: string;
  status: string;
}

export interface IIntelligenceMetrics {
  overallScore: number;
  riskExposure: number;
  fraudProbability: number;
  investigationPriority: string;
  confidence: number;
  lastUpdate: Date;
  nextUpdate: Date;
}
