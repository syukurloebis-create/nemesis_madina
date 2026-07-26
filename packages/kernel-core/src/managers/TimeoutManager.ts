/**
 * Timeout Manager - manages execution timeout
 * Independent - does not depend on other managers
 */
export interface TimeoutManager {
  /**
   * Start timeout timer
   */
  start(timeoutMs: number): void;
  
  /**
   * Check if timed out
   */
  isTimedOut(): boolean;
  
  /**
   * Cancel timeout
   */
  cancel(): void;
}