/**
 * NEMESIS V8+ - Services Barrel Export
 */

// Dashboard Service
export { default as dashboardService } from './dashboard';
export * from './dashboard';

// Intelligence Service
export { default as intelligenceService } from './intelligence';
export * from './intelligence';

// Decision Service
export { default as decisionService } from './decision';
export * from './decision';

// Alert Service
export { default as alertService } from './alert';
export * from './alert';

// API Modules - Re-export from api folder
export {
  casesApi,
  evidenceApi,
  graphApi,
  fraudApi,
  riskApi,
  intelligenceApi,
  procurementApi,
  recommendationApi,
} from './api';

// API Client
export { apiClient, default as client } from './api/client';

// Legacy Services
export { default as vendorService } from './vendorService';
export { default as websocketService } from './websocket';
export { default as procurementService } from './procurementService';

// Default export
export default {
  dashboard: dashboardService,
  intelligence: intelligenceService,
  decision: decisionService,
  alert: alertService,
};
