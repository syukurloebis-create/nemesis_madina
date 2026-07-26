import type { VersionMatrix } from '@nemesis/contracts-common';
import { StabilityLevel } from './StabilityLevel.js';
import { FreezeStatus } from './FreezeStatus.js';

export interface ContractMetadata {
  versions: VersionMatrix;
  stability: StabilityLevel;
  freezeStatus: FreezeStatus;
  owner: string;
}