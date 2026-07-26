export interface ContractProvenance {
  introducedByADR: string;
  introducedVersion: string;
  lastModifiedVersion: string;
  deprecatedSince?: string;
  supersededBy?: string;
  owner: string;
  reviewDate: string;
  reviewers: readonly string[];
  breakingChangeReason?: string;
  migrationGuide?: string;
}