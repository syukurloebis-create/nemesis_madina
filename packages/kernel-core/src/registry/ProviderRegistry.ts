import { RuntimeProvider } from '@nemesis/spi-provider';

/**
 * Provider registry - sealed after validation
 * Lifecycle: register → validate → freeze → read-only
 */
export interface ProviderRegistry {
  /**
   * Register a provider (before freeze only)
   */
  register<TInput, TOutput>(
    provider: RuntimeProvider<TInput, TOutput>
  ): void;
  
  /**
   * Validate all registered providers
   */
  validate(): RegistryValidationReport;
  
  /**
   * Freeze registry (read-only after)
   */
  freeze(): void;
  
  /**
   * Get a provider by ID (read-only after freeze)
   */
  get<TInput, TOutput>(id: string): RuntimeProvider<TInput, TOutput> | undefined;
  
  /**
   * List all providers (read-only after freeze)
   */
  list(): readonly RuntimeProvider<unknown, unknown>[];
  
  /**
   * Check if registry is frozen
   */
  isFrozen(): boolean;
}

/**
 * Registry validation report - detailed, not just boolean
 */
export interface RegistryValidationReport {
  /** Whether validation passed */
  passed: boolean;
  
  /** Validation warnings */
  warnings: readonly ValidationWarning[];
  
  /** Validation errors */
  errors: readonly ValidationError[];
  
  /** Duplicate capabilities found */
  duplicates: readonly DuplicateCapability[];
  
  /** Missing dependencies */
  missingDependencies: readonly MissingDependency[];
  
  /** Circular dependencies */
  cycles: readonly DependencyCycle[];
}

/**
 * Validation warning
 */
export interface ValidationWarning {
  providerId: string;
  message: string;
}

/**
 * Validation error
 */
export interface ValidationError {
  providerId: string;
  message: string;
}

/**
 * Duplicate capability
 */
export interface DuplicateCapability {
  providerId: string;
  capabilityId: string;
}

/**
 * Missing dependency
 */
export interface MissingDependency {
  providerId: string;
  dependencyId: string;
}

/**
 * Dependency cycle
 */
export interface DependencyCycle {
  providers: readonly string[];
}