import { ExecutionContext } from '@nemesis/contracts-execution';
import { ExecutionResult } from '@nemesis/contracts-execution';
import { RuntimeProvider } from '@nemesis/spi-provider';
import { ProgressTracker } from './ProgressTracker.js';
import { MetricsCollector } from './MetricsCollector.js';
import { TimeoutManager } from './TimeoutManager.js';
import { CancellationManager } from './CancellationManager.js';
import { EventPublisher } from './EventPublisher.js';

/**
 * Lifecycle Manager - manages execution lifecycle
 * Independent - does not depend on other managers
 */
export interface LifecycleManager<TInput, TOutput> {
  execute(
    provider: RuntimeProvider<TInput, TOutput>,
    input: TInput,
    context: ExecutionContext,
    progressTracker: ProgressTracker,
    metricsCollector: MetricsCollector,
    timeoutManager: TimeoutManager,
    cancellationManager: CancellationManager,
    eventPublisher: EventPublisher
  ): Promise<ExecutionResult<TOutput>>;
}