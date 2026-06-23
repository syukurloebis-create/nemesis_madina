// Use relative imports
import { casesApi, evidenceApi, graphApi, fraudApi, riskApi, recommendationApi, procurementApi } from '../api';
import { transformDashboardData } from './transformers';

export const dashboardService = {
  // Get complete dashboard data
  getDashboardData: async (caseId: string) => {
    const [
      cases,
      evidence,
      graph,
      fraud,
      risk,
      recommendations,
      procurement
    ] = await Promise.all([
      casesApi.getStats().catch(() => ({ data: null })),
      evidenceApi.getStats().catch(() => ({ data: null })),
      graphApi.getMetrics().catch(() => ({ data: null })),
      fraudApi.getStats().catch(() => ({ data: null })),
      // Use getCaseRiskExplanations instead of getTrend
      riskApi.getCaseRiskExplanations(caseId).catch(() => ({ data: null })),
      recommendationApi.getSummary().catch(() => ({ data: null })),
      procurementApi.getRUPStats().catch(() => ({ data: null })),
    ]);

    return transformDashboardData({
      cases: cases.data,
      evidence: evidence.data,
      graph: graph.data,
      fraud: fraud.data,
      risk: risk.data,
      recommendations: recommendations.data,
      procurement: procurement.data,
    });
  },

  // Get executive overview
  getExecutiveOverview: (caseId?: string) =>
    casesApi.getStats(),

  // Get strategic dashboard
  getStrategicDashboard: () =>
    casesApi.getStats(),
};

export * from './transformers';
export default dashboardService;
