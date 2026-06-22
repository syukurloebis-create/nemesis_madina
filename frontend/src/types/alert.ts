export interface IAlert {
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
  actions: IAlertAction[];
  metadata: Record<string, any>;
}

export interface IAlertAction {
  id: string;
  type: 'INVESTIGATE' | 'REVIEW' | 'ESCALATE' | 'IGNORE' | 'RESOLVE';
  label: string;
  description: string;
  handler: (alert: IAlert) => Promise<void>;
  priority: number;
}

export interface IAlertConfig {
  thresholds: {
    anomaly: number;
    collusion: number;
    fraud: number;
    risk: number;
  };
  cooldownPeriod: number;
  maxAlertsPerCase: number;
}
