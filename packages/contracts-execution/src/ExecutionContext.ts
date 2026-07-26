import { DurationMs, ExtensionBag } from '@nemesis/contracts-common';

/**
 * Immutable execution context split into granular capability contexts
 * All sub-contexts are readonly
 */
export interface ExecutionContext {
  /** Identity context */
  readonly identity: IdentityContext;
  
  /** Workspace context (granular) */
  readonly workspace: WorkspaceContext;
  
  /** Configuration context (granular) */
  readonly config: ConfigurationContext;
  
  /** Runtime context (granular) */
  readonly runtime: RuntimeContext;
  
  /** Policy context */
  readonly policy: PolicyContext;
  
  /** Cancellation context */
  readonly cancellation: CancellationContext;
  
  /** Metadata context (using Record for determinism) */
  readonly metadata: MetadataContext;
  
  /** Extension bag for provider-specific data */
  readonly extensions: ExtensionBag;
}

/**
 * Identity context - immutable
 */
export interface IdentityContext {
  readonly executionId: string;
  readonly providerId: string;
  readonly userId: string;
}

/**
 * Workspace context - granular capability
 */
export interface WorkspaceContext {
  readonly workspace: Workspace;
}

/**
 * Configuration context - granular capability
 */
export interface ConfigurationContext {
  readonly config: Configuration;
}

/**
 * Runtime context - granular capability
 */
export interface RuntimeContext {
  readonly runtime: RuntimeInfo;
}

/**
 * Policy context - immutable
 */
export interface PolicyContext {
  readonly timeout: DurationMs;
  readonly retry: RetryPolicy;
  readonly priority: PriorityPolicy;
}

/**
 * Cancellation context - immutable
 */
export interface CancellationContext {
  readonly token: CancellationToken;
  readonly reason?: string;
  readonly isCancelled: boolean;
}

/**
 * Metadata context - using Record for deterministic serialization
 * NOT using Map (non-deterministic order)
 */
export interface MetadataContext {
  readonly tags: readonly string[];
  readonly labels: Readonly<Record<string, string>>;
  readonly annotations: Readonly<Record<string, unknown>>;
}

// Type aliases for common types
export type Workspace = unknown;
export type Configuration = unknown;
export type RuntimeInfo = unknown;
export type RetryPolicy = unknown;
export type PriorityPolicy = unknown;
export type CancellationToken = unknown;
export type { DurationMs, ExtensionBag, Timestamp } from '@nemesis/contracts-common';