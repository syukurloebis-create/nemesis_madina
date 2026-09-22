import { describe, it, expect } from 'vitest';
import {
  deriveFreshness,
  displayAvailability,
  displayFreshness,
} from '../../types/semantic';

describe('Semantic Contract', () => {
  describe('DataAvailability display', () => {
    it('NOT_AVAILABLE ≠ NO_DATA ≠ AVAILABLE', () => {
      expect(displayAvailability('NOT_AVAILABLE')).toBe('Not Available');
      expect(displayAvailability('NO_DATA')).toBe('No Data');
      expect(displayAvailability('AVAILABLE')).toBe('Available');
      expect(displayAvailability('ERROR')).toBe('Error');
    });

    it('all values are distinct', () => {
      const values = [
        displayAvailability('NOT_AVAILABLE'),
        displayAvailability('NO_DATA'),
        displayAvailability('AVAILABLE'),
        displayAvailability('ERROR'),
      ];
      expect(new Set(values).size).toBe(4);
    });
  });

  describe('Freshness derivation', () => {
    it('recent timestamp = FRESH', () => {
      const recent = new Date(Date.now() - 60 * 1000).toISOString();
      expect(deriveFreshness(recent, 5)).toBe('FRESH');
    });

    it('old timestamp = STALE', () => {
      const old = new Date(Date.now() - 30 * 60 * 1000).toISOString();
      expect(deriveFreshness(old, 5)).toBe('STALE');
    });

    it('null = UNKNOWN', () => {
      expect(deriveFreshness(null)).toBe('UNKNOWN');
    });

    it('undefined = UNKNOWN', () => {
      expect(deriveFreshness(undefined)).toBe('UNKNOWN');
    });

    it('empty string = UNKNOWN', () => {
      expect(deriveFreshness('')).toBe('UNKNOWN');
    });

    it('invalid string = UNKNOWN', () => {
      expect(deriveFreshness('not-a-date')).toBe('UNKNOWN');
    });
  });

  describe('Freshness display', () => {
    it('all freshness states displayed', () => {
      expect(displayFreshness('FRESH')).toBe('Fresh');
      expect(displayFreshness('STALE')).toBe('Stale');
      expect(displayFreshness('UNKNOWN')).toBe('Unknown');
    });
  });
});
