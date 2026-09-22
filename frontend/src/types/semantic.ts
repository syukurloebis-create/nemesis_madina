// frontend/src/types/semantic.ts
// Semantic contract untuk data availability
// PENTING: Jangan konversi NOT_AVAILABLE menjadi 0

/**
 * Ketersediaan data dari backend.
 * 
 * - AVAILABLE:      Backend expose field, dan ada datanya
 * - NO_DATA:        Backend expose field, dan hasilnya kosong (0 records)
 * - NOT_AVAILABLE:  Backend TIDAK expose field ini (bukan 0!)
 * - ERROR:          Gagal fetch/parse
 */
export type DataAvailability =
  | 'AVAILABLE'
  | 'NO_DATA'
  | 'NOT_AVAILABLE'
  | 'ERROR';

/**
 * Freshness berdasarkan selisih generated_at dengan sekarang.
 * 
 * - FRESH:   Data dibuat < threshold (misal 5 menit)
 * - STALE:   Data dibuat > threshold
 * - UNKNOWN: Tidak ada generated_at
 */
export type Freshness =
  | 'FRESH'
  | 'STALE'
  | 'UNKNOWN';

/**
 * Helper: display label untuk DataAvailability
 */
export function displayAvailability(value: DataAvailability): string {
  switch (value) {
    case 'AVAILABLE':     return 'Available';
    case 'NO_DATA':       return 'No Data';
    case 'NOT_AVAILABLE': return 'Not Available';
    case 'ERROR':         return 'Error';
  }
}

/**
 * Helper: display label untuk Freshness
 */
export function displayFreshness(value: Freshness): string {
  switch (value) {
    case 'FRESH':   return 'Fresh';
    case 'STALE':   return 'Stale';
    case 'UNKNOWN': return 'Unknown';
  }
}

/**
 * Helper: derive freshness dari timestamp.
 */
export function deriveFreshness(
  generatedAt: string | null | undefined,
  thresholdMinutes: number = 5,
): Freshness {
  if (!generatedAt) return 'UNKNOWN';

  const parsed = new Date(generatedAt).getTime();
  if (isNaN(parsed)) return 'UNKNOWN';

  const ageMs = Date.now() - parsed;
  const thresholdMs = thresholdMinutes * 60 * 1000;

  return ageMs < thresholdMs ? 'FRESH' : 'STALE';
}

/**
 * Wrapper generik untuk nilai yang mungkin NOT_AVAILABLE.
 */
export interface MaybeAvailable<T> {
  availability: DataAvailability;
  value: T | null;
}

export function available<T>(value: T): MaybeAvailable<T> {
  return { availability: 'AVAILABLE', value };
}

export function notAvailable<T>(): MaybeAvailable<T> {
  return { availability: 'NOT_AVAILABLE', value: null };
}

export function noData<T>(): MaybeAvailable<T> {
  return { availability: 'NO_DATA', value: null };
}