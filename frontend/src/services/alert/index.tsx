import { alertsApi } from '../api';

export const alertService = {
  getAlerts: (params?: any) => alertsApi.getAlerts(params),
  getStats: (caseId: string) => alertsApi.getStats(caseId),
  acknowledge: (id: string) => alertsApi.acknowledge(id),
  resolve: (id: string) => alertsApi.resolve(id),
  escalate: (id: string) => alertsApi.escalate(id),
};
