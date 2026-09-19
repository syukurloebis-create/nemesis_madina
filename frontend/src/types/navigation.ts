/**
 * NEMESIS Navigation Contracts
 *
 * Phase 1 — Type-Safe Navigation
 *
 * Keep intelligence tab IDs and application route IDs explicit.
 * Do not use generic string for navigation state/actions.
 */

export type IntelligenceTabId =
  | 'overview'
  | 'risk'
  | 'graph'
  | 'fraud'
  | 'evidence'
  | 'timeline'
  | 'investigation'
  | 'recovery';

export type AppRouteId =
  | 'alerts'
  | 'investigation'
  | 'recovery'
  | 'procurement'
  | 'decisions';

export type DashboardActionId =
  | IntelligenceTabId
  | AppRouteId;
