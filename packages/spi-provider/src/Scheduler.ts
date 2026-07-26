import { LinearPlan } from './Planner.js';

/**
 * Scheduler SPI - "WHEN to do it"
 * Converts linear plan to DAG and schedules execution
 */
export interface Scheduler<TInput, TOutput> {
  schedule(plan: LinearPlan<TInput, TOutput>): Promise<ExecutionSchedule>;
}

/**
 * Execution schedule - only order
 * NOTE: Does NOT include resource allocation or duration estimation
 * Those are separate services
 */
export interface ExecutionSchedule {
  /** Plan ID */
  planId: string;
  
  /** Execution order (topological order) */
  order: readonly string[]; // Step IDs in execution order
}