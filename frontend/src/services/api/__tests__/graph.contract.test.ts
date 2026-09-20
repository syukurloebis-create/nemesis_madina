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

import {
  collusionResponseSchema,
  graphEdgeDTOSchema,
  graphMetricsSchema,
  graphNodeDTOSchema,
  graphSummarySchema,
  keyActorSchema,
} from './schemas/graph.schema';

import { loginForTests } from './helpers/auth';

const CASE_ID =
  'b4897392-87ab-4e7a-84b6-90228f3d1eb9';

describe('graphApi contract (F3 FROZEN)', () => {
  beforeAll(async () => {
    await loginForTests();
  });

  describe('getSummary', () => {
    it('matches GraphSummary schema', async () => {
      const summary = await graphApi.getSummary(CASE_ID);

      expect(() =>
        graphSummarySchema.parse(summary)
      ).not.toThrow();
    });

    it('matches frozen baseline 4177 / 2424', async () => {
      const summary = await graphApi.getSummary(CASE_ID);

      expect(summary.total_entities).toBe(4177);
      expect(summary.total_relationships).toBe(2424);
    });

    it('case_id matches request', async () => {
      const summary = await graphApi.getSummary(CASE_ID);

      expect(summary.case_id).toBe(CASE_ID);
    });
  });

  describe('getMetrics', () => {
    it('matches GraphMetrics schema', async () => {
      const metrics = await graphApi.getMetrics(CASE_ID);

      expect(() =>
        graphMetricsSchema.parse(metrics)
      ).not.toThrow();

      expect(metrics).toHaveProperty('density');
    });
  });

  describe('listEntities', () => {
    it('returns entities', async () => {
      const result = await graphApi.listEntities(
        CASE_ID,
        { limit: 5 },
      );

      expect(Array.isArray(result.entities)).toBe(true);
      expect(result.entities.length).toBeGreaterThan(0);
    });

    it('every entity matches frozen GraphNodeDTO', async () => {
      const result = await graphApi.listEntities(
        CASE_ID,
        { limit: 5 },
      );

      result.entities.forEach((entity, index) => {
        const parsed = graphNodeDTOSchema.safeParse(entity);

        if (!parsed.success) {
          throw new Error(
            `Entity ${index} failed schema:\n${JSON.stringify(
              parsed.error.issues,
              null,
              2,
            )}`,
          );
        }
      });
    });

    it('has no risk_score', async () => {
      const result = await graphApi.listEntities(
        CASE_ID,
        { limit: 5 },
      );

      result.entities.forEach(entity => {
        expect(entity).not.toHaveProperty('risk_score');
      });
    });

    it('has no confidence', async () => {
      const result = await graphApi.listEntities(
        CASE_ID,
        { limit: 5 },
      );

      result.entities.forEach(entity => {
        expect(entity).not.toHaveProperty('confidence');
      });
    });

    it('has no first_seen', async () => {
      const result = await graphApi.listEntities(
        CASE_ID,
        { limit: 5 },
      );

      result.entities.forEach(entity => {
        expect(entity).not.toHaveProperty('first_seen');
      });
    });
  });

  describe('listRelationships', () => {
    it('returns relationship array', async () => {
      const result = await graphApi.listRelationships(
        CASE_ID,
        { limit: 5 },
      );

      expect(Array.isArray(result.relationships)).toBe(true);
    });

    it('matches frozen GraphEdgeDTO', async () => {
      const result = await graphApi.listRelationships(
        CASE_ID,
        { limit: 5 },
      );

      result.relationships.forEach((relationship, index) => {
        const parsed = graphEdgeDTOSchema.safeParse(relationship);

        if (!parsed.success) {
          throw new Error(
            `Relationship ${index} failed schema:\n${JSON.stringify(
              parsed.error.issues,
              null,
              2,
            )}`,
          );
        }
      });
    });
  });

  describe('getKeyActors', () => {
    it('returns actors', async () => {
      const result = await graphApi.getKeyActors(CASE_ID, 5);

      expect(Array.isArray(result.actors)).toBe(true);
    });

    it('matches frozen KeyActor schema', async () => {
      const result = await graphApi.getKeyActors(CASE_ID, 5);

      result.actors.forEach((actor, index) => {
        const parsed = keyActorSchema.safeParse(actor);

        if (!parsed.success) {
          throw new Error(
            `Actor ${index} failed schema:\n${JSON.stringify(
              parsed.error.issues,
              null,
              2,
            )}`,
          );
        }
      });
    });

    it('has no risk_score', async () => {
      const result = await graphApi.getKeyActors(CASE_ID, 5);

      result.actors.forEach(actor => {
        expect(actor).not.toHaveProperty('risk_score');
      });
    });
  });

  describe('getCollusion', () => {
    it('matches CollusionResponse schema', async () => {
      const result = await graphApi.getCollusion(CASE_ID);

      expect(() =>
        collusionResponseSchema.parse(result)
      ).not.toThrow();
    });

    it('matches baseline: 4 collusion relationships', async () => {
      // Current runtime contract (structural count from
      // graph_relationships.COLLUSION). Historical frozen
      // provenance not established.
      const result = await graphApi.getCollusion(CASE_ID);

      expect(result.collusion_relationship_count).toBe(4);
    });
  });
});
