/**
 * Freeze status of a contract or ABI version
 */
export enum FreezeStatus {
  /** Initial state, may change */
  DRAFT = 'draft',
  
  /** Under review */
  CANDIDATE = 'candidate',
  
  /** Passed validation */
  VALIDATED = 'validated',
  
  /** Stable, no changes without ADR */
  FROZEN = 'frozen',
  
  /** Will be retired */
  DEPRECATED = 'deprecated',
  
  /** No longer active */
  RETIRED = 'retired'
}