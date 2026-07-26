import apiClient from './client';
import { casesApi } from './cases';
import { fraudApi } from './fraud';
import { evidenceApi } from './evidence';
import { graphApi } from './graph';
import { alertsApi } from './alerts';
import { vendorApi } from './vendors';
import { recommendationApi } from './recommendations';
import { procurementApi } from './procurement';
import { investigationsApi } from './investigations';
import { intelligenceApi } from './intelligence';
import { riskApi } from './risk';

// ============================================================
// MODULE EXPORTS
// ============================================================

export {
  casesApi,
  default as casesApiDefault
} from "./cases";

export {
  fraudApi
} from "./fraud";

export {
  graphApi
} from "./graph";

export {
  riskApi
} from "./risk";

export {
  evidenceApi
} from "./evidence";

export {
  alertsApi
} from "./alerts";

export {
  vendorApi,
  vendorApi as vendorsApi
} from "./vendors";

export {
  default as procurementApi
} from "./procurement";

export {
  investigationsApi,
  investigationsApi as investigationApi
} from "./investigations";

export {
  recommendationApi,
  recommendationApi as recommendationsApi
} from "./recommendations";

export {
  intelligenceApi
} from "./intelligence";

// ============================================================
// LEGACY COMPATIBILITY FUNCTIONS
// ============================================================

// EVIDENCE
export const listEvidence = (caseId?: string) =>
  apiClient.get("/api/v1/evidence", {
    params: caseId ? { case_id: caseId } : undefined
  });

export const uploadEvidence = (data: any) =>
  apiClient.post("/api/v1/evidence", data);

export const verifyEvidence = (id: string) =>
  apiClient.post(`/api/v1/evidence/${id}/verify`);

// GOVERNANCE
export const getPolicyImpact = (caseId: string) =>
  apiClient.get(`/api/v1/governance/policy-impact/${caseId}`);

// GRAPH - ADDITIONAL
export const getRelationships = (entityId?: string) =>
  apiClient.get("/api/v1/graph/relationships", {
    params: { entityId }
  });

export const getEntityGraph = (entityId: string) =>
  apiClient.get(`/api/v1/graph/entity/${entityId}`);

export const getCollusionCycles = () =>
  apiClient.get("/api/v1/graph/collusion-cycles");

// PROVENANCE
export const getProvenance = (id: string) =>
  apiClient.get(`/api/v1/provenance/${id}`);

// ============================================================
// LEGACY API FACADE
// ============================================================

export const api = {
  // Axios compatibility
  get: apiClient.get.bind(apiClient),
  post: apiClient.post.bind(apiClient),
  put: apiClient.put.bind(apiClient),
  delete: apiClient.delete.bind(apiClient),
  patch: apiClient.patch.bind(apiClient),
  request: apiClient.request.bind(apiClient),

  // CASES
  getCases: casesApi.getCases.bind(casesApi),
  getCase: casesApi.getCase.bind(casesApi),
  createCase: casesApi.createCase.bind(casesApi),
  updateCase: casesApi.updateCase.bind(casesApi),
  getCaseStats: casesApi.getStats.bind(casesApi),
  getRiskExplanations: casesApi.getRiskExplanations.bind(casesApi),
  deleteCase: (id: string) => apiClient.delete(`/api/v1/cases/${id}`),
  assignCase: (id: string, userId: string) => apiClient.post(`/api/v1/cases/${id}/assign`, { user_id: userId }),

  // EVIDENCE
  listEvidence,
  uploadEvidence,
  verifyEvidence,
  getEvidence: (caseId: string) => apiClient.get(`/api/v1/evidence?case_id=${caseId}`),
  getCustodyHistory: (evidenceId: string) => apiClient.get(`/api/v1/evidence/${evidenceId}/custody`),
  getCurrentCustodian: (evidenceId: string) => apiClient.get(`/api/v1/evidence/${evidenceId}/custodian`),

  // ALERTS
  getAlerts: alertsApi.getAlerts.bind(alertsApi),
  acknowledgeAlert: alertsApi.acknowledge.bind(alertsApi),
  resolveAlert: alertsApi.resolve.bind(alertsApi),
  escalateAlert: alertsApi.escalate.bind(alertsApi),

  // GRAPH
  getEntities: graphApi.getEntities.bind(graphApi),
  getMetrics: graphApi.getMetrics.bind(graphApi),
  getKeyActors: graphApi.getKeyActors.bind(graphApi),
  getCommunities: graphApi.getCommunities.bind(graphApi),
  getGraphStats: graphApi.getMetrics.bind(graphApi),
  getGraphCollusion: (caseId: string) => apiClient.get(`/api/v1/graph/collusion/${caseId}`),
  getRelationships,
  getEntityGraph,
  getCollusionCycles,

  // VENDORS
  getVendors: vendorApi.getSuspicious.bind(vendorApi),

  // PROCUREMENT
  getProcurementStats: procurementApi.getRUPStats.bind(procurementApi),

  // FRAUD
  getFraudStats: fraudApi.getStats.bind(fraudApi),
  getFraudPatterns: fraudApi.getPatterns.bind(fraudApi),

  // RISK
  getRiskStats: riskApi.getTrend.bind(riskApi),

  // INVESTIGATIONS
  getInvestigations: investigationsApi.getByCase.bind(investigationsApi),

  // INTELLIGENCE
  getIntelligence: intelligenceApi.getScore.bind(intelligenceApi),

  // RECOMMENDATIONS
  getRecommendations: recommendationApi.getSummary.bind(recommendationApi),

  // GOVERNANCE
  getPolicyImpact,

  // PROVENANCE
  getProvenance,

  // INTEGRITY
  verifyAllIntegrity: (caseId: string) => apiClient.get(`/api/v1/integrity/${caseId}/verify`),
  verifyCaseIntegrity: (caseId: string) => apiClient.get(`/api/v1/integrity/${caseId}/verify`),
  getEventChain: (caseId: string) => apiClient.get(`/api/v1/integrity/${caseId}/chain`),

  // TEMPORAL
  getEventTimeline: (caseId: string) => apiClient.get(`/api/v1/temporal/${caseId}/events`),
  getStateAtTime: (caseId: string, timestamp: string) => apiClient.get(`/api/v1/temporal/${caseId}?timestamp=${timestamp}`),
  compareVersions: (caseId: string, v1: number, v2: number) => 
    apiClient.get(`/api/v1/temporal/${caseId}/compare?version_a=${v1}&version_b=${v2}`),

  // AUDIT
  getAuditLogs: (params?: any) => apiClient.get('/api/v1/audit', { params }),
  getAuditTrail: (caseId: string) => apiClient.get(`/api/v1/audit/${caseId}`),

  // SYSTEM
  getSystemInfo: () => apiClient.get('/health'),
  verifyAll: () => apiClient.get('/api/v1/integrity/verify-all'),

  // EVENT
  getEvents: (caseId: string) => apiClient.get(`/api/v1/events/${caseId}`),
};

// ============================================================
// LEGACY NAMED EXPORTS
// ============================================================

// CASES
export const getCases = casesApi.getCases.bind(casesApi);
export const getCase = casesApi.getCase.bind(casesApi);
export const createCase = casesApi.createCase.bind(casesApi);
export const updateCase = casesApi.updateCase.bind(casesApi);
export const getCaseStats = casesApi.getStats.bind(casesApi);
export const getRiskExplanations = casesApi.getRiskExplanations.bind(casesApi);
export const deleteCase = (id: string) => apiClient.delete(`/api/v1/cases/${id}`);
export const assignCase = (id: string, userId: string) => apiClient.post(`/api/v1/cases/${id}/assign`, { user_id: userId });
export const getCaseTimeline = (
  id: string,
  limit?: number
) =>
  apiClient.get(
    `/api/v1/cases/${id}/timeline`,
    {
      params: {
        limit
      }
    }
  );

// EVIDENCE
export const getEvidence = (caseId: string) => apiClient.get(`/api/v1/evidence?case_id=${caseId}`);

// ALERTS
export const getAlerts = alertsApi.getAlerts.bind(alertsApi);
export const acknowledgeAlert = alertsApi.acknowledge.bind(alertsApi);
export const resolveAlert = alertsApi.resolve.bind(alertsApi);
export const escalateAlert = alertsApi.escalate.bind(alertsApi);

// GRAPH
export const getEntities = graphApi.getEntities.bind(graphApi);
export const getMetrics = graphApi.getMetrics.bind(graphApi);
export const getKeyActors = graphApi.getKeyActors.bind(graphApi);
export const getCommunities = graphApi.getCommunities.bind(graphApi);
export const getGraphStats = graphApi.getMetrics.bind(graphApi);
export const getGraphCollusion = (caseId: string) => apiClient.get(`/api/v1/graph/collusion/${caseId}`);

// PROCUREMENT
export const getProcurementStats = procurementApi.getRUPStats.bind(procurementApi);
export const getProcurementVendors = () => apiClient.get('/api/v1/procurement/vendors');

// RUP
export const getRUPStats = procurementApi.getRUPStats.bind(procurementApi);
export const getRUPData = (params?: any) => apiClient.get('/api/v1/rup', { params });
export const getRUPTahun = () => apiClient.get('/api/v1/rup/tahun');
export const getRUPStatus = () => apiClient.get('/api/v1/rup/status');
export const exportRUP = (format: string = 'csv') => apiClient.get(`/api/v1/rup/export?format=${format}`);

// FRAUD
export const getFraudStats = fraudApi.getStats.bind(fraudApi);
export const getFraudPatterns = fraudApi.getPatterns.bind(fraudApi);

// RISK
export const getRiskStats = riskApi.getTrend.bind(riskApi);

// INVESTIGATIONS
export const getInvestigations = investigationsApi.getByCase.bind(investigationsApi);

// INTELLIGENCE
export const getIntelligence = intelligenceApi.getScore.bind(intelligenceApi);

// RECOMMENDATIONS
export const getRecommendations = recommendationApi.getSummary.bind(recommendationApi);

// VENDORS
export const getVendors = vendorApi.getSuspicious.bind(vendorApi);

// GOVERNANCE

// PROVENANCE

// INTEGRITY
export const verifyAllIntegrity = (caseId: string) => apiClient.get(`/api/v1/integrity/${caseId}/verify`);
export const verifyCaseIntegrity = (caseId: string) => apiClient.get(`/api/v1/integrity/${caseId}/verify`);
export const getEventChain = (caseId: string) => apiClient.get(`/api/v1/integrity/${caseId}/chain`);

// TEMPORAL
export const getEventTimeline = (caseId: string) => apiClient.get(`/api/v1/temporal/${caseId}/events`);
export const getStateAtTime = (caseId: string, timestamp: string) => apiClient.get(`/api/v1/temporal/${caseId}?timestamp=${timestamp}`);
export const compareVersions = (caseId: string, v1: number, v2: number) => 
  apiClient.get(`/api/v1/temporal/${caseId}/compare?version_a=${v1}&version_b=${v2}`);

// AUDIT
export const getAuditLogs = (params?: any) => apiClient.get('/api/v1/audit', { params });
export const getAuditTrail = (caseId: string) => apiClient.get(`/api/v1/audit/${caseId}`);

// SYSTEM
export const getSystemInfo = () => apiClient.get('/health');

// EVENT
export const getEvents = (caseId: string) => apiClient.get(`/api/v1/events/${caseId}`);

export default api;

// ============================================================
// TEMPORAL STATE
// ============================================================

export const getTemporalState = (caseId: string, version?: string) =>
  apiClient.get(`/api/v1/cases/${caseId}/temporal-state`, {
    params: { version }
  });

export const getTrustLineage = (entityId: string) =>
  apiClient.get(`/api/v1/trust/lineage/${entityId}`);

// Add to api facade
// (api object already includes these via exports above)
