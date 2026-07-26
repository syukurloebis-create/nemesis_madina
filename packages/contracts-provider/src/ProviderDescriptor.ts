import { ProviderIdentity } from './ProviderIdentity.js';
import { CapabilityDescriptor } from './CapabilityDescriptor.js';
import { Dependency } from './Dependency.js';

/**
 * Provider descriptor - runtime contract (part of ABI)
 * NOTE: Does NOT contain provenance (ADR, reviewers, etc.)
 */
export interface ProviderDescriptor {
  /** Provider identity */
  identity: ProviderIdentity;
  
  /** Capabilities this provider offers */
  capabilities: readonly CapabilityDescriptor[];
  
  /** Dependencies this provider requires */
  dependencies: readonly Dependency[];
}