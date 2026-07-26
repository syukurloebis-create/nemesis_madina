import { ExecutionContext, ExecutionResult } from '@nemesis/contracts-execution';
import { RuntimeProvider } from '@nemesis/spi-provider';
import { LifecycleManager } from './managers/LifecycleManager.js';
import { ProgressTracker } from './managers/ProgressTracker.js';
import { MetricsCollector } from './managers/MetricsCollector.js';
import { TimeoutManager } from './managers/TimeoutManager.js';
import { CancellationManager } from './managers/CancellationManager.js';
import { EventPublisher } from './managers/EventPublisher.js';

/**
 * Execution Coordinator - orchestrates execution
 * Uses independent managers for each concern
 */
export interface ExecutionCoordinator<TInput, TOutput> {
  /**
   * Execute a provider
   * Coordinates lifecycle, progress, metrics, timeout, cancellation, events
   */
  execute(
    provider: RuntimeProvider<TInput, TOutput>,
    input: TInput,
    context: ExecutionContext
  ): Promise<ExecutionResult<TOutput>>;
}

/**
 * Default execution coordinator implementation
 * Uses independent managers (no dependencies between managers)
 */
export class DefaultExecutionCoordinator<TInput, TOutput>
  implements ExecutionCoordinator<TInput, TOutput>
{
  constructor(
    private readonly lifecycleManager: LifecycleManager<TInput, TOutput>,
    private readonly progressTracker: ProgressTracker,
    private readonly metricsCollector: MetricsCollector,
    private readonly timeoutManager: TimeoutManager,
    private readonly cancellationManager: CancellationManager,
    private readonly eventPublisher: EventPublisher
  ) {}
  
  async execute(
    provider: RuntimeProvider<TInput, TOutput>,
    input: TInput,
    context: ExecutionContext
  ): Promise<ExecutionResult<TOutput>> {
    // Coordinating managers - each manager is independent
    // No manager knows about other managers
    return this.lifecycleManager.execute(
      provider, input, context,
      this.progressTracker,
      this.metricsCollector,
      this.timeoutManager,
      this.cancellationManager,
      this.eventPublisher
    );
  }
}