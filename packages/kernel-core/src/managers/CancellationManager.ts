/**
 * Cancellation Manager - manages execution cancellation
 * Independent - does not depend on other managers
 */
export interface CancellationManager {
  /**
   * Check if cancelled
   */
  isCancelled(): boolean;
  
  /**
   * Get cancellation reason
   */
  getReason(): string | undefined;
  
  /**
   * Cancel execution
   */
  cancel(reason?: string): void;
}