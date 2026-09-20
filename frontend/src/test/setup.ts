import '@testing-library/jest-dom';
import { cleanup } from '@testing-library/react';
import { afterEach, vi } from 'vitest';

afterEach(() => {
  cleanup();
});

/**
 * Persistent in-memory localStorage mock.
 *
 * Important for API contract tests:
 * authService.setTokens() writes tokens to localStorage,
 * and apiClient later reads them back through getItem().
 */
const storage = new Map<string, string>();

const localStorageMock = {
  getItem: vi.fn((key: string) => {
    return storage.has(key)
      ? storage.get(key)!
      : null;
  }),

  setItem: vi.fn((key: string, value: string) => {
    storage.set(key, String(value));
  }),

  removeItem: vi.fn((key: string) => {
    storage.delete(key);
  }),

  clear: vi.fn(() => {
    storage.clear();
  }),

  key: vi.fn((index: number) => {
    return Array.from(storage.keys())[index] ?? null;
  }),

  get length() {
    return storage.size;
  },
};

global.localStorage = localStorageMock as any;

// IMPORTANT:
// Do NOT clear storage per-test.
// Contract tests set tokens once in beforeAll() and every
// test relies on those tokens being readable during execution.
// Vitest runs test files in isolated environments, so storage
// does not leak between test files.
//
// vi.clearAllMocks() is intentionally also omitted here to
// preserve the persistent localStorage mock implementation
// across the test file lifecycle.

// Do NOT mock global.fetch.
// Contract tests use real HTTP calls to the backend.

global.console = {
  ...console,
  error: vi.fn(),
  warn: vi.fn(),
  log: vi.fn(),
};
