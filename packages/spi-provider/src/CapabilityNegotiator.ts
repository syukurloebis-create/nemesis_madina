import { CapabilityDescriptor, CapabilitySet } from '@nemesis/contracts-provider';

/**
 * Capability negotiator SPI
 * Negotiates between requested and available capabilities
 */
export interface CapabilityNegotiator {
  /**
   * Negotiate capabilities
   * Returns detailed negotiation result
   */
  negotiate(
    requested: CapabilitySet,
    available: CapabilitySet
  ): Promise<NegotiationResult>;
}

/**
 * Detailed negotiation result
 * NOT just boolean - provides full context
 */
export interface NegotiationResult {
  /** Whether negotiation succeeded */
  success: boolean;

  /** Accepted capabilities */
  accepted: CapabilitySet;

  /** Rejected capabilities with reasons */
  rejected: readonly RejectedCapability[];

  /** Fallback capabilities used */
  fallback?: CapabilitySet;

  /** Conflicts detected */
  conflicts: readonly Conflict[];
}

/**
 * Rejected capability with reason
 */
export interface RejectedCapability {
  capability: CapabilityDescriptor;
  reason: string;
}

/**
 * Conflict between capabilities
 */
export interface Conflict {
  capabilityA: CapabilityDescriptor;
  capabilityB: CapabilityDescriptor;
  reason: string;
}