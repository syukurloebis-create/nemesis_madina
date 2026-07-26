import { Timestamp } from '@nemesis/contracts-common';
import type { EventMetadata } from './EventMetadata.js';

/**
 * Single event format for all platform events
 * Includes OpenTelemetry fields for future compatibility
 */
export interface EventEnvelope<T = unknown> {
  /** Unique event ID */
  id: string;
  
  /** Event timestamp */
  timestamp: Timestamp;
  
  /** Sequence number within stream (monotonic per execution) */
  sequenceNumber: number;
  
  /** Stream/execution ID */
  streamId: string;
  
  /** Correlation ID for tracing */
  correlationId?: string;
  
  /** Causation ID (parent event) */
  causationId?: string;
  
  /** OpenTelemetry trace ID */
  traceId?: string;
  
  /** OpenTelemetry span ID */
  spanId?: string;
  
  /** Producer of this event */
  producer: string;
  
  /** Type of event */
  eventType: string;
  
  /** Schema version of envelope */
  schemaVersion: string;
  
  /** Event version (payload version) */
  eventVersion: string;
  
  /** Event payload */
  payload: T;
  
  /** Event metadata */
  metadata: EventMetadata;
}