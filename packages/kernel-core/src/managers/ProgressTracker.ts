/**
 * Progress Tracker - tracks execution progress
 * Independent - does not depend on other managers
 */
export interface ProgressTracker {
  /**
   * Track progress step
   */
  track(step: string, progress: number): void;
  
  /**
   * Get current progress
   */
  getProgress(): ExecutionProgress;
}

/**
 * Execution progress
 */
export interface ExecutionProgress {
  percentage: number;
  step: string;
  completed: boolean;
}