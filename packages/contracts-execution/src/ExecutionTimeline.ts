import { Timestamp } from '@nemesis/contracts-common';

/**
 * Execution timeline
 */
export interface ExecutionTimeline {
  /** Start timestamp */
  startedAt: Timestamp;
  
  /** Completion timestamp */
  completedAt: Timestamp;
  
  /** Events in this execution */
  events: readonly ExecutionEvent[];
}

/**
 * Execution event
 */
export interface ExecutionEvent {
  /** Event timestamp */
  timestamp: Timestamp;
  
  /** Event type */
  type: string;
  
  /** Event data */
  data: unknown;
}