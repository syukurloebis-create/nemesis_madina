/**
 * @vitest-environment node
 *
 * Contract tests use real HTTP calls to the backend.
 * jsdom is NOT suitable for these API contract tests.
 */

import {
  beforeAll,
  describe,
  expect,
  it,
} from 'vitest';

import { riskApi } from '../risk';

import {
  riskExplanationSchema,
  riskStatsSchema,
} from './schemas/risk.schema';

import { loginForTests } from './helpers/auth';

const CASE_ID =
  'b4897392-87ab-4e7a-84b6-90228f3d1eb9';

describe('riskApi contract (Risk Engine v3 FROZEN)', () => {
  beforeAll(async () => {
    await loginForTests();
  });

  describe('getExplanations', () => {
    it('matches RiskExplanation schema', async () => {
      const explanation =
        await riskApi.getExplanations(CASE_ID);

      const result = riskExplanationSchema.safeParse(explanation);

      if (!result.success) {
        throw new Error(
          `RiskExplanation failed schema:\n${JSON.stringify(
            result.error.issues,
            null,
            2,
          )}`,
        );
      }
    });

    it('returns frozen baseline score 47.58', async () => {
      const explanation =
        await riskApi.getExplanations(CASE_ID);

      expect(explanation.score).toBe(47.58);
    });

    it('returns frozen baseline level MEDIUM', async () => {
      const explanation =
        await riskApi.getExplanations(CASE_ID);

      expect(explanation.risk_level).toBe('MEDIUM');
    });

    it('case_id matches request', async () => {
      const explanation =
        await riskApi.getExplanations(CASE_ID);

      expect(explanation.case_id).toBe(CASE_ID);
    });

    it('status is OK', async () => {
      const explanation =
        await riskApi.getExplanations(CASE_ID);

      expect(explanation.status).toBe('OK');
    });

    it('factors is an array', async () => {
      const explanation =
        await riskApi.getExplanations(CASE_ID);

      expect(Array.isArray(explanation.factors)).toBe(true);
    });

    it('recommendations is an array', async () => {
      const explanation =
        await riskApi.getExplanations(CASE_ID);

      expect(Array.isArray(explanation.recommendations)).toBe(true);
    });
  });

  describe('getStats', () => {
    it('matches RiskStats schema', async () => {
      const stats = await riskApi.getStats();

      expect(() => riskStatsSchema.parse(stats)).not.toThrow();
    });
  });
});
