/**
 * NEMESIS V8+ - Early Warning System Types
 */

export interface Alert {
  id: string;
  caseId: string;
  type: 'ANOMALY' | 'COLLUSION' | 'FRAUD' | 'RISK' | 'PATTERN' | 'RED_FLAG';
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  title: string;
  description: string;
  timestamp: Date;
  status: 'NEW' | 'ACKNOWLEDGED' | 'RESOLVED' | 'ESCALATED';
  source: string;
  confidence: number;
  evidence: string[];
  actions: AlertAction[];
  metadata: Record<string, any>;
  acknowledgedAt?: Date;
  acknowledgedBy?: string;
  resolvedAt?: Date;
  resolvedBy?: string;
  resolution?: string;
}

export interface AlertAction {
  id: string;
  type: 'INVESTIGATE' | 'REVIEW' | 'ESCALATE' | 'IGNORE' | 'RESOLVE';
  label: string;
  description: string;
  handler: (alert: Alert) => Promise<void>;
  priority: number;
  isEnabled: boolean;
  isVisible: boolean;
}

export interface AlertConfig {
  thresholds: {
    anomaly: number;
    collusion: number;
    fraud: number;
    risk: number;
  };
  cooldownPeriod: number; // milliseconds
  maxAlertsPerCase: number;
  autoAcknowledge: boolean;
  escalationTimeout: number; // milliseconds
}

export interface AlertFilter {
  type?: Alert['type'][];
  severity?: Alert['severity'][];
  status?: Alert['status'][];
  fromDate?: Date;
  toDate?: Date;
  search?: string;
}

export interface AlertStats {
  total: number;
  new: number;
  acknowledged: number;
  resolved: number;
  escalated: number;
  bySeverity: {
    LOW: number;
    MEDIUM: number;
    HIGH: number;
    CRITICAL: number;
  };
  byType: {
    ANOMALY: number;
    COLLUSION: number;
    FRAUD: number;
    RISK: number;
    PATTERN: number;
    RED_FLAG: number;
  };
  averageResolutionTime: number; // in hours
  escalationRate: number; // percentage
}

export interface AnomalyDetectionResult {
  caseId: string;
  score: number;
  threshold: number;
  isAnomaly: boolean;
  type: string;
  description: string;
  evidence: string[];
  timestamp: Date;
}

export interface PatternDetectionResult {
  caseId: string;
  patternId: string;
  patternType: string;
  description: string;
  confidence: number;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  entities: string[];
  evidence: string[];
  timestamp: Date;
}
