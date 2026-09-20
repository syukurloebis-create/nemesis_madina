import { z } from 'zod';

/**
 * Zod mirrors of the frozen F3 Graph DTO contract.
 *
 * These schemas OBSERVE the backend contract.
 * They do not define or calculate domain data.
 *
 * IMPORTANT: `.strict()` forbids extra keys — catches drift.
 */

export const graphNodeDTOSchema = z.object({
  id: z.string(),
  business_key: z.string(),
  name: z.string(),
  entity_type: z.string(),
  source_id: z.number().int().nullable(),
  extra_data: z.record(z.string(), z.unknown()),
}).strict();

export const graphEdgeDTOSchema = z.object({
  id: z.string().nullable(),
  source: z.string(),
  target: z.string(),
  relationship_type: z.string(),
  weight: z.number(),
  amount: z.number().nullable(),
  description: z.string().nullable(),
  extra_data: z.record(z.string(), z.unknown()),
}).strict();

export const graphPayloadSchema = z.object({
  case_id: z.string(),
  has_data: z.boolean(),
  nodes: z.array(graphNodeDTOSchema),
  edges: z.array(graphEdgeDTOSchema),
  summary: z.object({
    entities: z.number().int().nonnegative(),
    relationships: z.number().int().nonnegative(),
  }).strict(),
  version: z.number().nullable().optional(),
  checksum: z.string().nullable().optional(),
}).strict();

export const graphSummarySchema = z.object({
  case_id: z.string(),
  total_entities: z.number().int().nonnegative(),
  total_relationships: z.number().int().nonnegative(),
  entity_types: z.record(z.string(), z.number().int().nonnegative()),
  relationship_types: z.record(z.string(), z.number().int().nonnegative()),
}).strict();

export const graphMetricsSchema = graphSummarySchema.extend({
  density: z.number().nonnegative(),
}).strict();

export const keyActorSchema = z.object({
  id: z.string(),
  business_key: z.string(),
  name: z.string(),
  entity_type: z.string(),
  degree: z.number().int().nonnegative(),
}).strict();

export const collusionResponseSchema = z.object({
  case_id: z.string(),
  collusion_relationships: z.array(graphEdgeDTOSchema),
  collusion_relationship_count: z.number().int().nonnegative(),
  detection_backed: z.boolean(),
}).strict();
