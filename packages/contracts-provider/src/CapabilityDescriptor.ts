/**
 * Capability descriptor with feature flags
 * Feature flags enable evolution without ABI changes
 */

export interface CapabilityDescriptor {
  id: string;
  version: string;
  featureFlags: readonly string[];
}

