import { DurationMs } from '@nemesis/contracts-common';
import { ExecutionContext } from '@nemesis/contracts-execution';

export interface Planner<TInput, TOutput> {
  plan(input: TInput, context: ExecutionContext): Promise<LinearPlan<TInput, TOutput>>;
}

/**
 * Linear plan - simple, ordered steps
 * Kernel converts to DAG internally
 */
export interface LinearPlan<TInput, TOutput> {
  /** Unique plan ID */
  id: string;

  /** Steps in order */
  steps: readonly PlanStep<TInput, TOutput>[];

  /** Estimated duration */
  estimatedDuration: DurationMs;
}

/**
 * Plan step
 */
export interface PlanStep<TInput, TOutput> {
  /** Step ID */
  id: string;

  /** Step name */
  name: string;

  /** Step function */
  execute: (input: TInput, context: ExecutionContext) => Promise<TOutput>;
}