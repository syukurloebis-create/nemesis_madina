/**
 * Provider dependency
 */
export interface Dependency {
  /** Dependency ID */
  id: string;
  
  /** Minimum version required */
  minVersion: string;
  
  /** Maximum version supported */
  maxVersion?: string;
  
  /** Whether this dependency is required */
  required: boolean;
}