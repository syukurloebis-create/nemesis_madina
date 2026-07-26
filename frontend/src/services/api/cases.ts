import apiClient from './client';

export interface Case {
  id: string;
  title?: string;
  status?: string;
  riskScore?: number;
  [key: string]: any;
}

export interface CaseStats {
  total: number;
  open?: number;
  closed?: number;
  investigating?: number;
  avg_risk_score?: number;
}

export interface RiskExplanation {
  id?: string;
  reason?: string;
  score?: number;
}

export const casesApi = {
  getCases: (params?: any) => apiClient.get('/api/v1/cases', { params }),
  getCase: (id: string) => apiClient.get(`/api/v1/cases/${id}`),
  createCase: (data: any) => apiClient.post('/api/v1/cases', data),
  updateCase: (id: string, data: any) => apiClient.put(`/api/v1/cases/${id}`, data),
  getStats: () => apiClient.get('/api/v1/cases/stats'),
  getRiskExplanations: (caseId: string) => apiClient.get(`/api/v1/cases/${caseId}/risk-explanations`),
};

export const getAll = casesApi.getCases.bind(casesApi);
export default casesApi;
