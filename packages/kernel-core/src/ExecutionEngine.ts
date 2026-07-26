import { ExecutionContext, ExecutionResult } from '@nemesis/contracts-execution';
import { RuntimeProvider } from '@nemesis/spi-provider';
import { ExecutionCoordinator } from './ExecutionCoordinator.js';

/**
 * Execution Engine - FACADE ONLY
 * No state, no logic, pure delegation
 * All logic is delegated to ExecutionCoordinator and managers
 */
export interface ExecutionEngine<TInput, TOutput> {
  /**
   * Execute a provider
   * Pure delegation - no logic
   */
  execute(
    provider: RuntimeProvider<TInput, TOutput>,
    input: TInput,
    context: ExecutionContext
  ): Promise<ExecutionResult<TOutput>>;
}

/**
 * Execution Engine Facade implementation
 * Zero state, zero complexity, pure delegation
 */
export class DefaultExecutionEngine<TInput, TOutput>
  implements ExecutionEngine<TInput, TOutput>
{
  constructor(
    private readonly coordinator: ExecutionCoordinator<TInput, TOutput>
  ) {}
  
  async execute(
    provider: RuntimeProvider<TInput, TOutput>,
    input: TInput,
    context: ExecutionContext
  ): Promise<ExecutionResult<TOutput>> {
    // Pure delegation - no logic
    return this.coordinator.execute(provider, input, context);
  }
}