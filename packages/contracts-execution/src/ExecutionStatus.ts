/**
 * Core execution state - single source of truth
 * Providers can extend this with their own states
 */
export type CoreExecutionState = 
  | 'VALIDATING'
  | 'PREPARING'
  | 'EXECUTING'
  | 'COLLECTING'
  | 'COMPLETED'
  | 'FAILED'
  | 'CANCELLED'
  | 'TIMED_OUT';

/**
 * Execution status - alias for CoreExecutionState
 */
export type ExecutionStatus = CoreExecutionState;