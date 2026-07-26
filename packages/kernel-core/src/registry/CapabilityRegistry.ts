import { CapabilityDescriptor } from '@nemesis/contracts-provider';

/**
 * Capability registry - sealed after validation
 * Lifecycle: register → validate → freeze → read-only
 */
export interface CapabilityRegistry {
  /**
   * Register a capability (before freeze only)
   */
  register(capability: CapabilityDescriptor): void;
  
  /**
   * Validate all registered capabilities
   */
  validate(): CapabilityValidationReport;
  
  /**
   * Freeze registry (read-only after)
   */
  freeze(): void;
  
  /**
   * Get a capability by ID (read-only after freeze)
   */
  get(id: string): CapabilityDescriptor | undefined;
  
  /**
   * List all capabilities (read-only after freeze)
   */
  list(): readonly CapabilityDescriptor[];
  
  /**
   * Check if registry is frozen
   */
  isFrozen(): boolean;
}

/**
 * Capability validation report
 */
export interface CapabilityValidationReport {
  passed: boolean;
  conflicts: readonly CapabilityConflict[];
  warnings: readonly CapabilityWarning[];
}

/**
 * Capability conflict
 */
export interface CapabilityConflict {
  capabilityA: string;
  capabilityB: string;
  reason: string;
}

/**
 * Capability warning
 */
export interface CapabilityWarning {
  capabilityId: string;
  message: string;
}