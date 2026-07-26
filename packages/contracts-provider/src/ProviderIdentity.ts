/**
 * Provider identity - stable identifier
 */
export interface ProviderIdentity {
  /** Unique provider ID (stable, never changes) */
  id: string;
  
  /** Provider version (changes with releases) */
  version: string;
}