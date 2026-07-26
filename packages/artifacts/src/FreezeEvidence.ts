import { BaseArtifact } from './BaseArtifact.js';  // ✅ Correct
import { FreezeStatus } from '@nemesis/contracts-core';
import { ArchitectureFingerprint } from './ArchitectureFingerprint.js';

/**
 * Freeze evidence - audit trail for ABI freeze
 */
export interface FreezeEvidence extends BaseArtifact {
  /** ABI version being frozen */
  abiVersion: string;
  
  /** Freeze status */
  status: FreezeStatus;
  
  /** Freeze date */
  freezeDate: string; // ISO 8601
  
  /** Gate results */
  gates: GateResults;
  
  /** Fingerprint at freeze time */
  fingerprint: ArchitectureFingerprint;
  
  /** Invariants verified */
  invariants: readonly string[];
  
  /** Compatibility policy */
  compatibility: CompatibilityPolicy;
  
  /** Validated by */
  validatedBy: readonly string[];
}

/**
 * Gate results - all gates must pass
 */
export interface GateResults {
  abiDiff: boolean;
  layerValidation: boolean;
  determinism: boolean;
  coverage: boolean;
  invariants: boolean;
}

/**
 * Compatibility policy
 */
export interface CompatibilityPolicy {
  minimumABI: string;
  maximumABI: string;
  minimumSPI: string;
  maximumSPI: string;
}