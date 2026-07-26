/**
 * NEMESIS API - Legacy Compatibility Layer
 * This file provides backward compatibility for old components
 */
import apiClient from '../services/api/client';

// Create api instance with legacy methods
const api = apiClient;

// Add legacy methods to api instance
(api as any).verifyAllIntegrity = (caseId: string) =>
  apiClient.get(`/api/v1/integrity/${caseId}/verify`);

(api as any).acknowledgeAlert = (id: string) =>
  apiClient.post(`/api/v1/alerts/${id}/acknowledge`);

(api as any).resolveAlert = (id: string) =>
  apiClient.post(`/api/v1/alerts/${id}/resolve`);

(api as any).escalateAlert = (id: string) =>
  apiClient.post(`/api/v1/alerts/${id}/escalate`);

(api as any).getAuditLogs = (caseId?: string, params?: any) =>
  apiClient.get('/api/v1/audit', { params: { case_id: caseId, ...params } });

// Export api with all methods
export default api;
export { api };
