import { DurationMs, ExtensionBag } from '@nemesis/contracts-common';

/**
 * Execution metrics
 */
export interface ExecutionMetrics {
  /** Total duration in milliseconds */
  duration: DurationMs;

  /** Memory usage in MB (optional) */
  memory?: number;

  /** CPU usage percentage (optional) */
  cpu?: number;

  /** Custom metrics */
  custom: readonly CustomMetric[];

  /** Extension bag */
  extensions: ExtensionBag;
}

/**
 * Custom metric
 */
export interface CustomMetric {
  name: string;
  value: number;
  unit?: string;
}