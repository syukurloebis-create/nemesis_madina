// types/provenance.ts - Type definitions for Risk Reasoning
export interface RiskContributor {
  factor: string;
  score: number;
  weight: number;
  contribution: number;
  description: string;
  evidence?: string[];
  category?: 'primary' | 'secondary' | 'contextual';
}

export interface DecisionNode {
  order: number;
  type: 'evidence' | 'assertion' | 'risk_factor' | 'finding' | 'decision';
  data: any;
}

export interface ProvenanceData {
  case_id: string;
  case_title: string;
  status: string;
  risk_score: number;
  risk_level: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  workflow_stage: string;
  decision_chain: DecisionNode[];
  risk_contributors: RiskContributor[];
  summary: string;
  timestamp: string;
}

export interface RiskReasoningProps {
  caseId: string;
  className?: string;
  onInvestigate?: (caseId: string) => void;
  onGenerateReport?: (caseId: string) => void;
}
