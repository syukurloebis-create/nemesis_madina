// src/services/fraudApi.ts
import api from './api';
import type { 
  FraudPattern, 
  FraudPatternSummary,
  FraudSeverity,
  FraudStatus
} from '../types';

const fraudApi = {
  getFraudPatterns: (caseId: string) => {
    return api.get<FraudPattern[]>(`/api/v1/fraud/patterns/${caseId}`);
  },
  getFraudPattern: (patternId: string) => {
    return api.get<FraudPattern>(`/api/v1/fraud/patterns/${patternId}`);
  },
  getFraudAlerts: (caseId: string, status?: FraudStatus) => {
    const params = status ? { status } : {};
    return api.get<FraudPattern[]>(`/api/v1/fraud/alerts/${caseId}`, { params });
  },
  detectFraud: (caseId: string) => {
    return api.post<{ patterns: FraudPattern[]; summary: FraudPatternSummary }>(
      `/api/v1/fraud/detect/${caseId}`
    );
  },
  updatePatternStatus: (patternId: string, status: FraudStatus) => {
    return api.patch<FraudPattern>(`/api/v1/fraud/patterns/${patternId}`, { status });
  },
  getFraudStats: () => {
    return api.get<FraudPatternSummary>('/api/v1/fraud/stats');
  },
  getFraudRiskScore: (caseId: string) => {
    return api.get<{ riskScore: number; riskLevel: FraudSeverity }>(
      `/api/v1/fraud/risk/${caseId}`
    );
  },
  investigatePattern: (patternId: string, notes?: string) => {
    return api.post<{ success: boolean; message: string }>(
      `/api/v1/fraud/patterns/${patternId}/investigate`,
      { notes }
    );
  },
  dismissPattern: (patternId: string, reason?: string) => {
    return api.post<{ success: boolean; message: string }>(
      `/api/v1/fraud/patterns/${patternId}/dismiss`,
      { reason }
    );
  },
};

export default fraudApi;
