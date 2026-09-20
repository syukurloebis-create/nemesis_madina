import { z } from 'zod';

export const riskLevelSchema = z.enum([
  'LOW',
  'MEDIUM',
  'HIGH',
  'CRITICAL',
  'NO_DATA',
  'ERROR',
]);

export const riskExplanationStatusSchema = z.enum([
  'OK',
  'NO_DATA',
  'ERROR',
]);

export const riskComponentsSchema = z.object({
  findings_risk: z.number(),
  graph_risk: z.number(),
  fraud_risk: z.number(),
  evidence_risk: z.number(),
}).strict();

export const riskWeightsSchema = z.object({
  findings: z.number(),
  graph: z.number(),
  fraud: z.number(),
  evidence: z.number(),
}).strict();

export const riskExplanationSchema = z.object({
  case_id: z.string(),
  status: riskExplanationStatusSchema,
  score: z.number().nullable(),
  risk_level: riskLevelSchema,

  anomaly_score: z.number().optional(),
  collusion_score: z.number().optional(),
  financial_score: z.number().optional(),
  temporal_score: z.number().optional(),
  evidence_risk: z.number().optional(),

  factors: z.array(z.string()),
  recommendations: z.array(z.string()),

  calculated_at: z.string().nullable(),
  timestamp: z.string().optional(),
}).strict();

export const riskStatsSchema = z.object({
  status: z.enum(['OK', 'NO_DATA', 'ERROR']),
  total: z.number().int().nonnegative(),
  critical: z.number().int().nonnegative(),
  high: z.number().int().nonnegative(),
  medium: z.number().int().nonnegative(),
  low: z.number().int().nonnegative(),
  avg_score: z.number(),
  timestamp: z.string(),
  message: z.string().optional(),
}).strict();

export const riskCalculateResultSchema = z.object({
  status: z.enum(['OK', 'ERROR']),
  case_id: z.string(),
  result: z.object({
    score: z.number(),
    level: riskLevelSchema,
    components: riskComponentsSchema,
    weights: riskWeightsSchema,
    factors: z.array(z.string()),
    recommendations: z.array(z.string()),
  }).strict(),
}).strict();
