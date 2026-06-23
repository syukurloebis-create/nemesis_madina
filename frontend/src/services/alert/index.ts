// Use relative imports
import { fraudApi, graphApi, riskApi } from '../api';

export const alertService = {
  // Get alerts for a case
  getAlerts: async (caseId: string) => {
    try {
      const [fraudAlerts, graphAlerts, riskAlerts] = await Promise.all([
        fraudApi.getSignals(caseId).catch(() => []),
        graphApi.getCollusion(caseId).catch(() => []),
        riskApi.getExplanations(caseId).catch(() => []),
      ]);

      return {
        fraud: fraudAlerts || [],
        graph: graphAlerts || [],
        risk: riskAlerts || [],
      };
    } catch (error) {
      console.error('[AlertService] Error:', error);
      return { fraud: [], graph: [], risk: [] };
    }
  },

  // Get active alerts
  getActiveAlerts: async (caseId: string) => {
    const alerts = await alertService.getAlerts(caseId);
    // Filter active alerts
    return alerts;
  },
};

export default alertService;
