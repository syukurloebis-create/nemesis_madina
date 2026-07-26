import { ContractMetadata } from './ContractMetadata.js';

/**
 * Contract descriptor - runtime contract metadata
 * NOTE: This is a runtime contract, NOT a governance artifact
 * Contains only metadata needed at runtime
 */
export interface ContractDescriptor {
  /** Unique contract identifier */
  id: string;

  /** Human-readable name */
  name: string;

  /** Contract description */
  description: string;

  /** Contract metadata (runtime only) */
  metadata: ContractMetadata;
}