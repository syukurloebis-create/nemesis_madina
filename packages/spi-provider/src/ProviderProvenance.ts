/**
 * Provider provenance - governance metadata
 * NOT part of runtime ABI
 */
export interface ProviderProvenance {
  /** ADR(s) that introduced this provider */
  adr: readonly string[];

  /** Baseline version this provider is built against */
  baseline: string;

  /** Architecture fingerprint at time of provider creation */
  fingerprint: string;

  /** Design decision document link */
  designDecision?: string;
}

/**
 * Build metadata
 */
export interface BuildMetadata {
  /** Build timestamp */
  builtAt: string;

  /** Build tool version */
  buildTool: string;

  /** CI pipeline ID */
  pipelineId?: string;

  /** Git commit hash */
  commitHash?: string;
}