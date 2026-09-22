// frontend/src/utils/format.ts
//
// Shared display-format helpers for Phase C.
//
// Semantic meaning remains in types/semantic.ts.
// This module only handles DISPLAY formatting.
//
// Usage:
//   formatTimestamp(iso)   → 'YYYY-MM-DD HH:MM:SS UTC' | '—'
//   freshnessStyle(fr)     → Tailwind class string for badge

import type { Freshness } from '../types/semantic';

/**
 * Format ISO timestamp to "YYYY-MM-DD HH:MM:SS UTC".
 * Returns "—" for null/undefined/invalid values.
 */
export function formatTimestamp(
  iso: string | null | undefined,
): string {
  if (!iso) return '—';

  const parsed = new Date(iso);
  if (Number.isNaN(parsed.getTime())) return '—';

  const year = parsed.getUTCFullYear();
  const month = String(parsed.getUTCMonth() + 1).padStart(2, '0');
  const day = String(parsed.getUTCDate()).padStart(2, '0');
  const hours = String(parsed.getUTCHours()).padStart(2, '0');
  const minutes = String(parsed.getUTCMinutes()).padStart(2, '0');
  const seconds = String(parsed.getUTCSeconds()).padStart(2, '0');

  return `${year}-${month}-${day} ${hours}:${minutes}:${seconds} UTC`;
}

/**
 * Tone class for freshness badge.
 */
export function freshnessStyle(freshness: Freshness): string {
  switch (freshness) {
    case 'FRESH':
      return 'text-green-400 border-green-500/30 bg-green-500/10';

    case 'STALE':
      return 'text-yellow-400 border-yellow-500/30 bg-yellow-500/10';

    case 'UNKNOWN':
      return 'text-gray-400 border-gray-500/30 bg-gray-500/10';

    default:
      return 'text-gray-400 border-gray-500/30 bg-gray-500/10';
  }
}
