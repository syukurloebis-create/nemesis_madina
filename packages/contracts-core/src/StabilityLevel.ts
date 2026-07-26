export enum StabilityLevel {
  /** Internal use only - not for external providers */
  INTERNAL = 'internal',

  /** Not stable, may change without notice */
  EXPERIMENTAL = 'experimental',

  /** Stable interface, may change with minor version */
  PREVIEW = 'preview',

  /** Backward compatible, stable */
  STABLE = 'stable',

  /** Will be removed in future version */
  DEPRECATED = 'deprecated',

  /** No longer available */
  REMOVED = 'removed'
}