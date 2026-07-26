import { EventEnvelope } from '@nemesis/contracts-events';

/**
 * Event Publisher - publishes execution events
 * Independent - does not depend on other managers
 */
export interface EventPublisher {
  /**
   * Publish an event
   */
  publish<T>(event: EventEnvelope<T>): void;
  
  /**
   * Get all published events
   */
  getEvents(): readonly EventEnvelope<unknown>[];
  
  /**
   * Clear published events
   */
  clear(): void;
}