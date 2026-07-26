import { ExecutionMetrics } from '@nemesis/contracts-execution';

/**
 * Metrics Collector - collects execution metrics
 * Independent - does not depend on other managers
 */
export interface MetricsCollector {
  /**
   * Start collecting metrics
   */
  start(): void;
  
  /**
   * Stop collecting metrics
   */
  stop(): void;
  
  /**
   * Get collected metrics
   */
  getMetrics(): ExecutionMetrics;
  
  /**
   * Record custom metric
   */
  recordCustom(name: string, value: number, unit?: string): void;
}