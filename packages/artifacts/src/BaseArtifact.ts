import { VersionMatrix } from '@nemesis/contracts-common';

export interface BaseArtifact {
  schemaVersion: string;
  artifactType: string;
  generatedBy: string;
  generatedAt: string;
}

export interface VersionedArtifact extends BaseArtifact {
  versions: VersionMatrix;
}