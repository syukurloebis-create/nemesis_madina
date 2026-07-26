// types/fraud.ts - Fraud Pattern Detection Types

export const FraudSeverity = {
  CRITICAL: 'CRITICAL',
  HIGH: 'HIGH',
  MEDIUM: 'MEDIUM',
  LOW: 'LOW'
} as const;

export type FraudSeverityType = typeof FraudSeverity[keyof typeof FraudSeverity];

export const FraudTrend = {
  RISING: 'RISING',
  STABLE: 'STABLE',
  DECLINING: 'DECLINING'
} as const;

export type FraudTrendType = typeof FraudTrend[keyof typeof FraudTrend];

export const FraudStatus = {
  ACTIVE: 'ACTIVE',
  INVESTIGATING: 'INVESTIGATING',
  RESOLVED: 'RESOLVED',
  FALSE_POSITIVE: 'FALSE_POSITIVE'
} as const;

export type FraudStatusType = typeof FraudStatus[keyof typeof FraudStatus];

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
  severity: FraudSeverityType;
  confidence: number;
  trend: FraudTrendType;
  status: FraudStatusType;
  indicators: FraudIndicator[];
  cases: string[];
  affected_entities: string[];
  detected_at: string;
  updated_at: string;
  evidence_count: number;
}

export interface FraudPatternSummary {
  total: number;
  by_severity: Record<FraudSeverityType, number>;
  by_status: Record<FraudStatusType, number>;
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
  severity: FraudSeverityType;
  examples: string[];
  detection_rules: string[];
}

// Export default untuk fallback
export default {
  FraudSeverity,
  FraudTrend,
  FraudStatus,
};
