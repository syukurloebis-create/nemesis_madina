/**
 * NEMESIS V8+ - Intelligence Types
 * Untuk Risk Reasoning Panel & AIStatusBar
 */

export interface IntelligenceData {
  // Overall intelligence
  score: number;
  confidence: number;
  timestamp: Date;
  
  // Risk Analysis
  risk: {
    score: number;
    level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
    factors: RiskFactor[];
    explanations: string[];
  };
  
  // Graph Intelligence
  graph: {
    entities: number;
    relationships: number;
    communities: number;
    keyActors: KeyActor[];
    collusionRisk: number;
  };
  
  // Evidence Intelligence
  evidence: {
    total: number;
    verified: number;
    pending: number;
    confidence: number;
  };
  
  // Fraud Detection
  fraud: {
    patterns: number;
    signals: number;
    alerts: number;
    confidence: number;
  };
  
  // Reasoning Chain
  reasoning: ReasoningStep[];
  
  // Recommendations
  recommendations: IntelligenceRecommendation[];
}

export interface RiskFactor {
  id: string;
  category: string;
  description: string;
  score: number;
  weight: number;
  confidence: number;
  evidence: string[];
  impact: string;
}

export interface KeyActor {
  id: string;
  name: string;
  type: string;
  influence: number;
  riskScore: number;
  role: string;
  connections: number;
}

export interface ReasoningStep {
  id: string;
  type: 'OBSERVATION' | 'ANALYSIS' | 'CONCLUSION' | 'RECOMMENDATION';
  title: string;
  description: string;
  confidence: number;
  evidence: string[];
  timestamp: Date;
  relatedEntities: string[];
}

export interface IntelligenceRecommendation {
  id: string;
  title: string;
  description: string;
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  confidence: number;
  impact: number;
  effort: number;
  actions: string[];
  category: 'PREVENTIVE' | 'DETECTIVE' | 'CORRECTIVE';
}
