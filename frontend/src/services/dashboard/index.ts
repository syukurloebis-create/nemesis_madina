/**
 * Dashboard Service - Fixed
 */
import apiClient from '../api/client';

export const getDashboardStats = async () => {
  try {
    const response: any = await apiClient.get('/api/v1/dashboard/stats');
    const data = response?.data || response || {};
    
    return {
      alerts: data.active_alerts ?? 0,
      entities: data.total_entities ?? 0,
      relationships: data.total_relationships ?? 0,
    };
  } catch {
    return {
      alerts: 0,
      entities: 0,
      relationships: 0,
    };
  }
};

export const dashboardService = {
  getDashboardData: async (caseId?: string) => {
    const params = caseId ? { case_id: caseId } : {};
    const [cases, fraud, graph, risk] = await Promise.all([
      apiClient.get('/api/v1/cases/stats', { params }),
      apiClient.get('/api/v1/fraud/stats', { params }),
      apiClient.get('/api/v1/graph/metrics', { params }),
      apiClient.get('/api/v1/risk/stats', { params }),
    ]);
    return {
      cases: cases?.data || cases || {},
      fraud: fraud?.data || fraud || {},
      graph: graph?.data || graph || {},
      risk: risk?.data || risk || {},
    };
  },
};

export default dashboardService;
