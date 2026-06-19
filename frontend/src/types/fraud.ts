// types/fraud.ts - Fraud Pattern Detection Types

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

export interface FraudPatternProps {
  className?: string;
  onInvestigate?: (patternId: string) => void;
  onDismiss?: (patternId: string) => void;
}

export interface PatternLibraryItem {
  id: string;
  name: string;
  description: string;
  category: string;
  severity: FraudSeverity;
  examples: string[];
  detection_rules: string[];
}
