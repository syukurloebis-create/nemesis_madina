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

import { graphApi } from '../graph';
import { riskApi } from '../risk';

import { loginForTests } from './helpers/auth';

const CASE_ID =
  'b4897392-87ab-4e7a-84b6-90228f3d1eb9';

describe('NEMESIS CP2.5.1 baseline (FROZEN)', () => {
  beforeAll(async () => {
    await loginForTests();
  });

  it('Risk baseline: 47.58 MEDIUM', async () => {
    const explanation =
      await riskApi.getExplanations(CASE_ID);

    expect(explanation.score).toBe(47.58);
    expect(explanation.risk_level).toBe('MEDIUM');
  });

  it('Graph baseline: 4177 entities', async () => {
    const summary = await graphApi.getSummary(CASE_ID);

    expect(summary.total_entities).toBe(4177);
  });

  it('Graph baseline: 2424 relationships', async () => {
    const summary = await graphApi.getSummary(CASE_ID);

    expect(summary.total_relationships).toBe(2424);
  });

  it('Collusion baseline: 4 structural relationships', async () => {
    // NOTE: Current runtime contract value (4) from
    // graph_relationships.COLLUSION. Historical frozen
    // provenance is not established; treated as observable
    // baseline from backend contract.
    //
    // Analytical collusion_detections table is separate (= 0).

    const collusion = await graphApi.getCollusion(CASE_ID);

    expect(collusion.collusion_relationship_count).toBe(4);
  });
});
