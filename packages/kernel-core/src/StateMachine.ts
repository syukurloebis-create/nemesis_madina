import { CoreExecutionState } from '@nemesis/contracts-execution';

/**
 * Generic state machine in kernel
 * Single source of truth for state transitions
 * No provider-specific knowledge
 */
export class StateMachine<S extends string> {
  private current: S;
  private readonly transitions: Readonly<Record<S, readonly S[]>>;
  private readonly terminalStates: readonly S[];
  private readonly nonCancellableStates: readonly S[];

  constructor(
    initialState: S,
    transitions: Readonly<Record<S, readonly S[]>>,
    terminalStates: readonly S[],
    nonCancellableStates: readonly S[]
  ) {
    this.current = initialState;
    this.transitions = transitions;
    this.terminalStates = terminalStates;
    this.nonCancellableStates = nonCancellableStates;
  }

  getState(): S {
    return this.current;
  }

  canTransition(next: S): boolean {
    const allowed = this.transitions[this.current] || [];
    return allowed.includes(next);
  }

  transition(next: S): void {
    if (!this.canTransition(next)) {
      throw new Error(`Invalid transition from ${this.current} to ${next}`);
    }
    this.current = next;
  }

  isTerminal(): boolean {
    return this.terminalStates.includes(this.current);
  }

  canCancel(): boolean {
    return !this.nonCancellableStates.includes(this.current);
  }
}

export function createExecutionStateMachine(
  initialState: CoreExecutionState
): StateMachine<CoreExecutionState> {
  const transitions: Readonly<Record<CoreExecutionState, readonly CoreExecutionState[]>> = {
    VALIDATING: ['PREPARING', 'FAILED', 'CANCELLED'],
    PREPARING: ['EXECUTING', 'FAILED', 'CANCELLED'],
    EXECUTING: ['COLLECTING', 'FAILED', 'CANCELLED', 'TIMED_OUT'],
    COLLECTING: ['COMPLETED', 'FAILED', 'CANCELLED', 'TIMED_OUT'],
    COMPLETED: [],
    FAILED: [],
    CANCELLED: [],
    TIMED_OUT: []
  };

  const terminalStates: CoreExecutionState[] = ['COMPLETED', 'FAILED', 'CANCELLED', 'TIMED_OUT'];
  const nonCancellableStates: CoreExecutionState[] = ['COMPLETED', 'FAILED', 'CANCELLED', 'TIMED_OUT'];

  return new StateMachine(initialState, transitions, terminalStates, nonCancellableStates);
}