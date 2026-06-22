// src/services/decisionApi.ts
import api from './api';
import type { Decision, DecisionTrace } from '../types';

const decisionApi = {
  getDecisions: (caseId: string) => {
    return api.get<Decision[]>(`/api/v1/decisions/${caseId}`);
  },
  getDecision: (decisionId: string) => {
    return api.get<Decision>(`/api/v1/decisions/${decisionId}`);
  },
  getDecisionTrace: (decisionId: string) => {
    return api.get<DecisionTrace[]>(`/api/v1/decisions/${decisionId}/trace`);
  },
  createDecision: (data: Partial<Decision>) => {
    return api.post<Decision>('/api/v1/decisions', data);
  },
  updateDecisionStatus: (decisionId: string, status: Decision['status']) => {
    return api.patch<Decision>(`/api/v1/decisions/${decisionId}`, { status });
  },
};

export default decisionApi;
