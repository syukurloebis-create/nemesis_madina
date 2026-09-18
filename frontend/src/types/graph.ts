// frontend/src/types/graph.ts
// Graph F3 Contract v1 (FROZEN)
//
// Baseline: 4177 entities | 2424 relationships
// Commit: 579e020 | Tag: f3-graph-intelligence-v1
//
// Domain truth (F3.4-A / F3.4-B):
//   GraphNode has EXACTLY 5 fields:
//     business_key, entity_type, name, source_id, extra_data
//   NO risk_score, NO confidence, NO id.
//   Key actor ranking is STRUCTURAL (degree).

// ─── Node / Edge ─────────────────────────────────────────────────────

export interface GraphNode {
  id: string;                       // == business_key (alias untuk frontend)
  business_key: string;
  name: string;
  entity_type: string;
  source_id: number | null;         // int | null (domain truth)
  extra_data: Record<string, unknown>;
  // NOTE: NO risk_score, NO confidence.
}

export interface GraphEdge {
  id: string | null;                // often null (domain truth)
  source: string;                   // business_key
  target: string;                   // business_key
  relationship_type: string;
  weight: number;
  amount: number | null;
  description: string | null;
  extra_data: Record<string, unknown>;
}

// ─── Responses ───────────────────────────────────────────────────────

export interface GraphPayload {
  case_id: string;
  has_data: boolean;
  nodes: GraphNode[];
  edges: GraphEdge[];
  summary: {
    entities: number;
    relationships: number;
  };
  version?: number | null;
  checksum?: string | null;
}

export interface GraphSummary {
  case_id: string;
  total_entities: number;
  total_relationships: number;
  entity_types: Record<string, number>;
  relationship_types: Record<string, number>;
}

export interface GraphMetrics extends GraphSummary {
  density: number;
}

// ─── Key actors ──────────────────────────────────────────────────────

export interface GraphKeyActor {
  id: string;
  business_key: string;
  name: string;
  entity_type: string;
  degree: number;
  // NOTE: NO risk_score, NO confidence (structural ranking only).
}

export interface GraphKeyActorsResponse {
  case_id: string;
  actors: GraphKeyActor[];
  count: number;
}

// ─── Collusion ───────────────────────────────────────────────────────

/**
 * Collusion semantics (F3.3 LOCKED):
 *   COLLUSION relationship edges  ≠  COLLUSION detections
 *   detection_backed = false when `collusion_detections` table is empty.
 */
export interface GraphCollusionResponse {
  case_id: string;
  collusion_relationships: GraphEdge[];
  collusion_relationship_count: number;
  detection_backed: boolean;
}

// ─── Paginated/bounded list responses ────────────────────────────────

/**
 * Bounded list response (v1).
 * NOTE: This is NOT pagination. Backend loads case-scoped GraphAggregate
 * and applies `[:limit]` at the application read boundary.
 * No `offset`, no `total`.
 */
export interface GraphEntitiesResponse {
  case_id: string;
  entities: GraphNode[];
  count: number;
  limit: number;
}

export interface GraphRelationshipsResponse {
  case_id: string;
  relationships: GraphEdge[];
  count: number;
  limit: number;
}