import { ExecutionContext, ExecutionMetrics } from '@nemesis/contracts-execution';
import { Diagnostic } from '@nemesis/contracts-diagnostics';
import { ProviderDescriptor } from '@nemesis/contracts-provider';
import { ProviderManifest } from './ProviderManifest.js';

export interface RuntimeProvider<TInput, TOutput> {
  /**
   * Get provider descriptor (ABI contract)
   * This is part of the runtime contract
   */
  getDescriptor(): ProviderDescriptor;

  /**
   * Get provider manifest (build artifact)
   * Contains governance metadata (provenance, signature, etc.)
   */
  getManifest(): ProviderManifest;

  /**
   * Validate input
   */
  validate(input: TInput, context: ExecutionContext): Promise<Diagnostic[]>;

  /**
   * Prepare for execution
   */
  prepare(input: TInput, context: ExecutionContext): Promise<void>;

  /**
   * Execute the provider
   */
  execute(input: TInput, context: ExecutionContext): Promise<TOutput>;

  /**
   * Collect metrics after execution
   */
  collect(input: TInput, output: TOutput, context: ExecutionContext): Promise<ExecutionMetrics>;

  /**
   * Dispose resources
   */
  dispose(input: TInput, output?: TOutput, context?: ExecutionContext): Promise<void>;
}