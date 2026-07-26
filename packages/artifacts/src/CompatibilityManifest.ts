import { BaseArtifact } from './BaseArtifact.js';  // ✅ Correct
import { CompatibilityPolicy } from './FreezeEvidence.js';

export enum CompatibilityStatus {
  COMPATIBLE = 'compatible',
  INCOMPATIBLE = 'incompatible',
  UNKNOWN = 'unknown'
}

export interface ProviderCompatibility {
  id: string;
  version: string;
  abi: string;
  spi: string;
  kernel: string;
  status: CompatibilityStatus;  // ✅ Use enum
}

/**
 * Compatibility manifest - provider compatibility matrix
 */
export interface CompatibilityManifest extends BaseArtifact {
  /** ABI version */
  abiVersion: string;
  
  /** Compatibility policy */
  policy: CompatibilityPolicy;
  
  /** Provider compatibility entries */
  providers: Record<string, ProviderCompatibility>;
}
