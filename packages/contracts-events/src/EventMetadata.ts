import { EventCategory } from './EventCategory.js';
import { ExtensionBag } from '@nemesis/contracts-common';

export enum EventImportance {
  DEBUG = 'debug',
  INFO = 'info',
  WARNING = 'warning',
  ERROR = 'error',
  CRITICAL = 'critical'
}

export interface EventMetadata {
  category: EventCategory;
  replayable: boolean;
  importance: EventImportance;  // ✅ Use enum
  extensions: ExtensionBag;
}
