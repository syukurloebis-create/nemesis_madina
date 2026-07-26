import { BaseArtifact } from './BaseArtifact.js';
import { ArchitectureFingerprint } from './ArchitectureFingerprint.js';
import { FreezeStatus, StabilityLevel } from '@nemesis/contracts-core';

/**
 * Architecture baseline - frozen state of ABI
 */
export interface ArchitectureBaseline extends BaseArtifact {
  /** Baseline version */
  version: string;

  /** ABI version */
  abiVersion: string;

  /** Freeze status */
  status: FreezeStatus;

  /** Stability level */
  stability: StabilityLevel;

  /** Contracts in this baseline */
  contracts: readonly string[];

  /** Fingerprint of this baseline */
  fingerprint: ArchitectureFingerprint;
}