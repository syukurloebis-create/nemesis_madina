/**
 * Error category enum - not free text
 * Deterministic error classification for Golden Dataset comparison
 */
export enum ErrorCategory {
  VALIDATION = 'validation',
  EXECUTION = 'execution',
  TIMEOUT = 'timeout',
  CANCELLATION = 'cancellation',
  PROVIDER = 'provider',
  CONFIGURATION = 'configuration',
  DEPENDENCY = 'dependency',
  RESOURCE = 'resource',
  SECURITY = 'security',
  AUTHORIZATION = 'authorization',
  AUTHENTICATION = 'authentication',
  NETWORK = 'network',
  IO = 'io',
  INTERNAL = 'internal'
}