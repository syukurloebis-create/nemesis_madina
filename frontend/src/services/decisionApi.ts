// services/decisionApi.ts - Decision Support API
import api from './api';
import { Decision, DecisionSummary, DecisionStatus } from '../types/decision';

export const decisionApi = {
  // Get all decisions
  getDecisions: async (caseId?: string): Promise<Decision[]> => {
    const url = caseId ? `/api/v1/decisions?case_id=${caseId}` : '/api/v1/decisions';
    const response = await api.get(url);
    return response.data;
  },

  // Get decision by ID
  getDecision: async (id: string): Promise<Decision> => {
    const response = await api.get(`/api/v1/decisions/${id}`);
    return response.data;
  },

  // Get decision summary
  getDecisionSummary: async (): Promise<DecisionSummary> => {
    const response = await api.get('/api/v1/decisions/summary');
    return response.data;
  },

  // Create decision
  createDecision: async (data: Partial<Decision>): Promise<Decision> => {
    const response = await api.post('/api/v1/decisions', data);
    return response.data;
  },

  // Update decision status
  updateDecisionStatus: async (id: string, status: DecisionStatus): Promise<Decision> => {
    const response = await api.put(`/api/v1/decisions/${id}/status`, { status });
    return response.data;
  },

  // Update decision
  updateDecision: async (id: string, data: Partial<Decision>): Promise<Decision> => {
    const response = await api.put(`/api/v1/decisions/${id}`, data);
    return response.data;
  },

  // Get decision justification
  getDecisionJustification: async (id: string): Promise<any> => {
    const response = await api.get(`/api/v1/decisions/${id}/justification`);
    return response.data;
  },

  // Execute decision action
  executeDecision: async (id: string): Promise<any> => {
    const response = await api.post(`/api/v1/decisions/${id}/execute`);
    return response.data;
  }
};

export default decisionApi;
