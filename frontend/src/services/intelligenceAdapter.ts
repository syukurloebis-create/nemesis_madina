// frontend/src/services/intelligenceAdapter.ts

import { IntelligenceDashboardResponse } from '../types/intelligence';
import {
  DataAvailability,
  Freshness,
  deriveFreshness,
} from '../types/semantic';

// ============================================================
// NORMALIZED FRAUD CONTRACT
// ============================================================

export interface FraudPattern {
  type: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW';
  confidence: number;
  detectedAt: string;
  validated: boolean;
  description: string;
}

// ============================================================
// NORMALIZED GRAPH CONTRACT
// ============================================================

export interface StructuralHub {
  entityId: string;
  entityType: string;
  name: string;
  relationshipCount: number;
}

export interface GraphIntelligenceModel {
  entities: number;
  relationships: number;

  structuralHubs: {
    availability: DataAvailability;
    items: StructuralHub[];
  };

  engine: string;
  engine_status: string;
}

// ============================================================
// NORMALIZED INVESTIGATION ITEM
//
// IMPORTANT:
// Root `findings[]` from dashboard intelligence is a mixed-engine
// observation/feed containing fraud_engine, risk_engine,
// graph_engine and procurement_engine entries.
//
// It is NOT the same thing as the canonical Risk Engine v3
// `findings_risk` component.
// ============================================================

export interface InvestigationItem {
  id: string;
  source: string;
  severity: string;
  title: string;
  description: string;
  confidence: number;
  detectedAt: string;
  metadata: Record<string, unknown> | null;
}

// ============================================================
// NORMALIZED INTELLIGENCE MODEL
// ============================================================

export interface IntelligenceModel {
  case_id: string;

  fraud: {
    overall_risk: string;
    score: number;
    active_alerts: number;
    high_confidence: number;
    total_patterns: number;
    validated_patterns: number;
    highest_confidence: number;
    average_confidence: number;

    patterns: FraudPattern[];

    // Dashboard endpoint does NOT expose clusters.
    clustersAvailability: DataAvailability;

    /**
     * Legacy — may be undefined.
     * Preserved for backward compatibility with older dashboard schema.
     *
     * @deprecated Removed in Phase B.
     */
    signals?: {
      hub_entities?: any[];
      shared_package_patterns?: any[];
      method_similarity_patterns?: any[];
    };

    engine: string;
    engine_status: string;
  };

  risk: {
    score: number;
    level: string;

    // Legacy/supporting fields.
    anomaly_score: number;
    collusion_score: number;
    financial_score: number;
    recommendations: string[];

    /**
     * Legacy — may be undefined.
     * @deprecated
     */
    case_status?: string;

    engine: string;
    engine_status: string;
  };

  graph: GraphIntelligenceModel;

  evidence: {
    score: number;
    level: string;
    total: number;
    verified: number;
    rejected: number;
    pending: number;
    avg_trust: number;
    avg_confidence: number;

    /**
     * Legacy — may be undefined.
     * @deprecated Removed in Phase B.
     */
    confidence_level?: string;
    components?: {
      trust_component?: number;
      verification_component?: number;
      integrity_component?: number;
      confidence_component?: number;
    };
    custody_events?: number;
    recommendation?: string;

    availability: DataAvailability;

    engine: string;
    engine_status: string;
  };

  findings: {
    total: number;
    critical: number;
    high: number;
    medium: number;

    /**
     * Preferred semantic name for investigation feed items.
     *
     * These are MIXED-ENGINE observations, NOT canonical
     * Risk Engine v3 `findings_risk` component values.
     */
    items: InvestigationItem[];

    /**
     * @deprecated Use `items` for new code.
     *
     * Preserved as alias for backward compatibility during Phase A
     * migration. Will be removed in Phase B once all consumers
     * are migrated.
     */
    findings: InvestigationItem[];
  };

  generatedAt: string | null;
  requestId: string | null;
  traceId: string | null;
  freshness: Freshness;
}

// ============================================================
// HELPERS
// ============================================================

function normalizeSeverity(
  value: unknown,
): FraudPattern['severity'] {
  const normalized = String(value ?? 'LOW').toUpperCase();

  if (
    normalized === 'CRITICAL' ||
    normalized === 'HIGH' ||
    normalized === 'MEDIUM' ||
    normalized === 'LOW'
  ) {
    return normalized;
  }

  return 'LOW';
}

function normalizeFraudPattern(raw: any): FraudPattern {
  return {
    type: String(raw?.type ?? 'unknown'),
    severity: normalizeSeverity(raw?.severity),
    confidence:
      typeof raw?.confidence === 'number'
        ? raw.confidence
        : 0,
    detectedAt:
      typeof raw?.detected_at === 'string'
        ? raw.detected_at
        : '',
    validated: Boolean(raw?.validated),
    description: String(raw?.description ?? ''),
  };
}

function normalizeInvestigationItem(
  raw: any,
): InvestigationItem {
  return {
    id: String(raw?.id ?? ''),
    source: String(raw?.source ?? ''),
    severity: String(raw?.severity ?? ''),
    title: String(raw?.title ?? ''),
    description: String(raw?.description ?? ''),
    confidence:
      typeof raw?.confidence === 'number'
        ? raw.confidence
        : 0,
    detectedAt:
      typeof raw?.detected_at === 'string'
        ? raw.detected_at
        : '',
    metadata:
      raw?.metadata &&
      typeof raw.metadata === 'object'
        ? raw.metadata
        : null,
  };
}

function normalizeRecommendations(
  value: unknown,
): string[] {
  if (!Array.isArray(value)) return [];

  return value.filter(
    (item): item is string =>
      typeof item === 'string',
  );
}

// ============================================================
// NORMALIZER
// ============================================================

export function normalizeIntelligence(
  data?: IntelligenceDashboardResponse | null,
): IntelligenceModel {
  // ----------------------------------------------------------
  // EMPTY / ERROR-SAFE MODEL
  // ----------------------------------------------------------

  if (!data) {
    const emptyFindings: InvestigationItem[] = [];

    return {
      case_id: '',

      fraud: {
        overall_risk: 'UNKNOWN',
        score: 0,
        active_alerts: 0,
        high_confidence: 0,
        total_patterns: 0,
        validated_patterns: 0,
        highest_confidence: 0,
        average_confidence: 0,
        patterns: [],
        clustersAvailability: 'NOT_AVAILABLE',
        signals: undefined,
        engine: '',
        engine_status: '',
      },

      risk: {
        score: 0,
        level: 'UNKNOWN',
        anomaly_score: 0,
        collusion_score: 0,
        financial_score: 0,
        recommendations: [],
        case_status: undefined,
        engine: '',
        engine_status: '',
      },

      graph: {
        entities: 0,
        relationships: 0,

        structuralHubs: {
          availability: 'NOT_AVAILABLE',
          items: [],
        },

        engine: '',
        engine_status: '',
      },

      evidence: {
        score: 0,
        level: '',
        total: 0,
        verified: 0,
        rejected: 0,
        pending: 0,
        avg_trust: 0,
        avg_confidence: 0,
        confidence_level: undefined,
        components: undefined,
        custody_events: undefined,
        recommendation: undefined,
        availability: 'NO_DATA',
        engine: '',
        engine_status: '',
      },

      findings: {
        total: 0,
        critical: 0,
        high: 0,
        medium: 0,
        items: emptyFindings,
        findings: emptyFindings,
      },

      generatedAt: null,
      requestId: null,
      traceId: null,
      freshness: 'UNKNOWN',
    };
  }

  // ----------------------------------------------------------
  // FRAUD PATTERNS
  //
  // Backend field is `type`, NOT `pattern_type`.
  // ----------------------------------------------------------

  const rawPatterns = Array.isArray(data.fraud?.patterns)
    ? data.fraud.patterns
    : [];

  const patterns = rawPatterns.map(
    normalizeFraudPattern,
  );

  const clustersAvailability: DataAvailability =
    // There is no `clusters` field in the dashboard response.
    'NOT_AVAILABLE';

  // ----------------------------------------------------------
  // FINDINGS / INVESTIGATION FEED
  //
  // IMPORTANT:
  // root findings[] is mixed-engine feed.
  // Preserve root aggregate counts separately.
  // ----------------------------------------------------------

  const rawFindings = Array.isArray(data.findings)
    ? data.findings
    : [];

  const items = rawFindings.map(
    normalizeInvestigationItem,
  );

  // ----------------------------------------------------------
  // EVIDENCE AVAILABILITY
  //
  // Field exists in backend contract.
  // Empty evidence => NO_DATA, not NOT_AVAILABLE.
  // ----------------------------------------------------------

  const evidenceAvailability: DataAvailability =
    data.evidence
      ? data.evidence.total > 0
        ? 'AVAILABLE'
        : 'NO_DATA'
      : 'NOT_AVAILABLE';

  // ----------------------------------------------------------
  // FRESHNESS
  // ----------------------------------------------------------

  const generatedAt =
    typeof data.generated_at === 'string'
      ? data.generated_at
      : null;

  // ----------------------------------------------------------
  // NORMALIZED MODEL
  // ----------------------------------------------------------

  return {
    case_id: data.case_id,

    fraud: {
      overall_risk:
        data.fraud?.overall_risk ?? 'UNKNOWN',

      score:
        typeof data.fraud?.score === 'number'
          ? data.fraud.score
          : 0,

      active_alerts:
        typeof data.fraud?.active_alerts === 'number'
          ? data.fraud.active_alerts
          : 0,

      high_confidence:
        typeof data.fraud?.high_confidence === 'number'
          ? data.fraud.high_confidence
          : 0,

      total_patterns:
        typeof data.fraud?.total_patterns === 'number'
          ? data.fraud.total_patterns
          : patterns.length,

      validated_patterns:
        typeof data.fraud?.validated_patterns === 'number'
          ? data.fraud.validated_patterns
          : 0,

      highest_confidence:
        typeof data.fraud?.highest_confidence === 'number'
          ? data.fraud.highest_confidence
          : 0,

      average_confidence:
        typeof data.fraud?.average_confidence === 'number'
          ? data.fraud.average_confidence
          : 0,

      patterns,

      clustersAvailability,

      signals:
        (data.fraud as any)?.signals,

      engine:
        data.fraud?.engine ?? '',

      engine_status:
        data.fraud?.engine_status ?? '',
    },

    risk: {
      score:
        typeof data.risk?.score === 'number'
          ? data.risk.score
          : 0,

      level:
        data.risk?.level ?? 'UNKNOWN',

      // Explicitly preserved as legacy/supporting fields.
      anomaly_score:
        typeof data.risk?.anomaly_score === 'number'
          ? data.risk.anomaly_score
          : 0,

      collusion_score:
        typeof data.risk?.collusion_score === 'number'
          ? data.risk.collusion_score
          : 0,

      financial_score:
        typeof data.risk?.financial_score === 'number'
          ? data.risk.financial_score
          : 0,

      recommendations:
        normalizeRecommendations(
          data.risk?.recommendations,
        ),

      case_status:
        typeof (data.risk as any)?.case_status === 'string'
          ? (data.risk as any).case_status
          : undefined,

      engine:
        data.risk?.engine ?? '',

      engine_status:
        data.risk?.engine_status ?? '',
    },

    graph: {
      entities:
        typeof data.graph?.entities === 'number'
          ? data.graph.entities
          : 0,

      relationships:
        typeof data.graph?.relationships === 'number'
          ? data.graph.relationships
          : 0,

      // Dashboard intelligence endpoint does not expose
      // a structural-hub list. Do not synthesize one.
      structuralHubs: {
        availability: 'NOT_AVAILABLE',
        items: [],
      },

      engine:
        data.graph?.engine ?? '',

      engine_status:
        data.graph?.engine_status ?? '',
    },

    evidence: {
      score:
        typeof data.evidence?.score === 'number'
          ? data.evidence.score
          : 0,

      level:
        data.evidence?.level ?? '',

      total:
        typeof data.evidence?.total === 'number'
          ? data.evidence.total
          : 0,

      verified:
        typeof data.evidence?.verified === 'number'
          ? data.evidence.verified
          : 0,

      rejected:
        typeof data.evidence?.rejected === 'number'
          ? data.evidence.rejected
          : 0,

      pending:
        typeof data.evidence?.pending === 'number'
          ? data.evidence.pending
          : 0,

      avg_trust:
        typeof data.evidence?.avg_trust === 'number'
          ? data.evidence.avg_trust
          : 0,

      avg_confidence:
        typeof data.evidence?.avg_confidence === 'number'
          ? data.evidence.avg_confidence
          : 0,

      confidence_level:
        typeof (data.evidence as any)?.confidence_level === 'string'
          ? (data.evidence as any).confidence_level
          : undefined,

      components:
        (data.evidence as any)?.components,

      custody_events:
        typeof (data.evidence as any)?.custody_events === 'number'
          ? (data.evidence as any).custody_events
          : undefined,

      recommendation:
        typeof (data.evidence as any)?.recommendation === 'string'
          ? (data.evidence as any).recommendation
          : undefined,

      availability: evidenceAvailability,

      engine:
        data.evidence?.engine ?? '',

      engine_status:
        data.evidence?.engine_status ?? '',
    },

    findings: {
      // These are root response aggregates.
      // They are NOT recomputed from the mixed-engine array.
      total:
        typeof data.total === 'number'
          ? data.total
          : 0,

      critical:
        typeof data.critical === 'number'
          ? data.critical
          : 0,

      high:
        typeof data.high === 'number'
          ? data.high
          : 0,

      medium:
        typeof data.medium === 'number'
          ? data.medium
          : 0,

      items,

      // Compatibility alias during Phase A migration.
      findings: items,
    },

    generatedAt,

    requestId:
      typeof data.request_id === 'string'
        ? data.request_id
        : null,

    traceId:
      typeof data.trace_id === 'string'
        ? data.trace_id
        : null,

    freshness: deriveFreshness(
      generatedAt,
      5,
    ),
  };
}
