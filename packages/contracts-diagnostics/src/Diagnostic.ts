import { ErrorCategory } from './ErrorCategory.js';

/**
 * Diagnostic with category - uses "causes" for nested diagnostics
 * Consistent with Java/.NET/Rust terminology
 */
export interface Diagnostic {
  /** Error category (enum, not free text) */
  category: ErrorCategory;
  
  /** Provider-specific error code */
  code: string;
  
  /** Human-readable message */
  message: string;
  
  /** Nested diagnostics (causes) */
  causes: readonly Diagnostic[];
  
  /** Additional context */
  extensions: Record<string, unknown>;
}

/**
 * Extension bag for arbitrary data
 */
export interface ExtensionBag {
  [key: string]: unknown;
}