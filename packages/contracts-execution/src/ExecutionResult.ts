import { ExecutionStatus } from './ExecutionStatus.js';
import { ExecutionMetrics } from './ExecutionMetrics.js';
import { ExecutionTimeline } from './ExecutionTimeline.js';
import { Diagnostic } from '@nemesis/contracts-diagnostics';
import { ExtensionBag } from '@nemesis/contracts-common';

export enum ChecksumAlgorithm {
  SHA256 = 'SHA256',
  SHA512 = 'SHA512'
}

export interface ExecutionResult<T> {
  status: ExecutionStatus;
  output?: T;
  metrics: ExecutionMetrics;
  diagnostics: ExecutionDiagnostics;
  timeline: ExecutionTimeline;
  checksum: string;
  checksumAlgorithm: ChecksumAlgorithm;  // ✅ Use enum
  resultVersion: string;
  extensions: ExtensionBag;
}

/**
 * Execution diagnostics
 */
export interface ExecutionDiagnostics {
  /** Error diagnostics */
  errors: readonly Diagnostic[];
  
  /** Warning diagnostics */
  warnings: readonly Diagnostic[];
  
  /** Info diagnostics */
  infos: readonly Diagnostic[];
  
  /** Extension bag */
  extensions: ExtensionBag;
}