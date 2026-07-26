import { alertsApi } from '../api';
import wsService from '../websocket';

export const alertService = {
  // Core methods
  getAlerts: (params?: any) => alertsApi.getAlerts(params),
  getStats: (caseId: string) => alertsApi.getStats(caseId),
  acknowledge: (id: string) => alertsApi.acknowledge(id),
  resolve: (id: string) => alertsApi.resolve(id),
  escalate: (id: string) => alertsApi.escalate(id),

  // LEGACY COMPATIBILITY - named methods
  acknowledgeAlert: (id: string) => alertsApi.acknowledge(id),
  resolveAlert: (id: string) => alertsApi.resolve(id),
  escalateAlert: (id: string) => alertsApi.escalate(id),

  // WebSocket compatibility
  on: (event: string, handler: any) => {
    return wsService?.on?.(event, handler) || (() => {});
  },
  removeAllListeners: () => {
    // No-op for compatibility
  },
  emit: (event: string, data: any) => {
    wsService?.send?.({ type: event, payload: data });
  },
};

export default alertService;
