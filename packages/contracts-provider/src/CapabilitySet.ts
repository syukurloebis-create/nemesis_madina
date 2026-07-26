import { CapabilityDescriptor } from './CapabilityDescriptor.js';

export interface CapabilitySet {
  capabilities: readonly CapabilityDescriptor[];
}