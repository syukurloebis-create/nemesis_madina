import { describe, it, expect } from 'vitest';
import { normalizeIntelligence } from '../intelligenceAdapter';

// Frozen case fixture — captures actual backend response shape
// for case b4897392-87ab-4e7a-84b6-90228f3d1eb9
const FROZEN_CASE = 'b4897392-87ab-4e7a-84b6-90228f3d1eb9';

const frozenBackendResponse: any = {
  case_id: FROZEN_CASE,
  total: 9,
  critical: 0,
  high: 2,
  medium: 5,
  findings: [
    {
      id: 'acc6d1a4-0474-41ce-bc39-85246f2791a6',
      source: 'fraud_engine',
      severity: 'HIGH',
      title: 'Fraud Pattern: transaction_anomaly',
      description: 'Multiple high-value transactions detected',
      confidence: 0.855,
      detected_at: '2026-09-08T04:32:03.218867Z',
      metadata: { pattern_type: 'transaction_anomaly', validated: false },
    },
    {
      id: 'dc8050d4-fa7a-40b0-8337-c0253d29d021',
      source: 'risk_engine',
      severity: 'MEDIUM',
      title: 'Risk Level: MEDIUM',
      description: 'Risk score: 47.6',
      confidence: 0.4758,
      detected_at: '2026-09-22T02:09:53.806707Z',
      metadata: { score: 47.58 },
    },
    // (7 more items — abbreviated for test)
  ],
  fraud: {
    overall_risk: 'HIGH',
    score: 75.26666666666667,
    active_alerts: 2,
    high_confidence: 2,
    total_patterns: 3,
    validated_patterns: 0,
    highest_confidence: 85.5,
    average_confidence: 75.26666666666667,
    patterns: [
      {
        type: 'transaction_anomaly',
        severity: 'HIGH',
        confidence: 85.5,
        detected_at: '2026-09-08T04:32:03.218867Z',
        validated: false,
        description: 'Multiple high-value transactions detected',
      },
      {
        type: 'vendor_collusion',
        severity: 'HIGH',
        confidence: 78.3,
        detected_at: '2026-09-08T04:32:03.218867Z',
        validated: false,
        description: 'Unusual vendor-vendor connections found',
      },
      {
        type: 'network_anomaly',
        severity: 'MEDIUM',
        confidence: 62.0,
        detected_at: '2026-09-08T04:32:03.218867Z',
        validated: false,
        description: 'Central node with excessive connections',
      },
    ],
    engine: 'fraud',
    engine_status: 'OK',
  },
  graph: {
    entities: 4177,
    relationships: 2424,
    engine: 'graph',
    engine_status: 'OK',
  },
  risk: {
    score: 47.58,
    level: 'MEDIUM',
    anomaly_score: 0.0,
    collusion_score: 0.0,
    financial_score: 0.0,
    recommendations: [
      '📋 Schedule follow-up review',
      '🔎 Monitor for escalation',
      '🔗 Investigate network connections for collusion patterns',
    ],
    engine: 'risk',
    engine_status: 'OK',
  },
  evidence: {
    score: 0.0,
    level: 'NO_DATA',
    total: 0,
    verified: 0,
    rejected: 0,
    pending: 0,
    avg_trust: 0.0,
    avg_confidence: 0.0,
    engine: 'evidence',
    engine_status: 'OK',
  },
  recovery: {
    business_state: 'READY',
    actions: [],
    engine: 'recovery',
    engine_status: 'OK',
  },
  confidence: 59.48,
  status: 'operational',
  generated_at: '2026-09-22T02:09:53.806633Z',
  request_id: 'test-request-id',
  trace_id: 'test-trace-id',
  version: {
    build: 'dev',
    commit: 'dev',
    branch: 'main',
  },
};

describe('Intelligence Adapter — Frozen Case', () => {
  describe('Fraud normalization', () => {
    it('extracts 3 patterns from `type` field (not `pattern_type`)', () => {
      const model = normalizeIntelligence(frozenBackendResponse);

      expect(model.fraud.patterns).toHaveLength(3);
      expect(model.fraud.patterns[0].type).toBe('transaction_anomaly');
      expect(model.fraud.patterns[1].type).toBe('vendor_collusion');
      expect(model.fraud.patterns[2].type).toBe('network_anomaly');
    });

    it('preserves severity, confidence, description', () => {
      const model = normalizeIntelligence(frozenBackendResponse);

      expect(model.fraud.patterns[0].severity).toBe('HIGH');
      expect(model.fraud.patterns[0].confidence).toBe(85.5);
      expect(model.fraud.patterns[0].validated).toBe(false);
      expect(model.fraud.patterns[0].description).toBeTruthy();
    });

    it('clusters availability = NOT_AVAILABLE (backend does not expose)', () => {
      const model = normalizeIntelligence(frozenBackendResponse);

      expect(model.fraud.clustersAvailability).toBe('NOT_AVAILABLE');
    });

    it('preserves aggregate counts', () => {
      const model = normalizeIntelligence(frozenBackendResponse);

      expect(model.fraud.total_patterns).toBe(3);
      expect(model.fraud.overall_risk).toBe('HIGH');
      expect(model.fraud.active_alerts).toBe(2);
    });
  });

  describe('Graph normalization', () => {
    it('preserves 4177 entities / 2424 relationships', () => {
      const model = normalizeIntelligence(frozenBackendResponse);

      expect(model.graph.entities).toBe(4177);
      expect(model.graph.relationships).toBe(2424);
    });

    it('structural hubs = NOT_AVAILABLE (no backend endpoint)', () => {
      const model = normalizeIntelligence(frozenBackendResponse);

      expect(model.graph.structuralHubs.availability).toBe('NOT_AVAILABLE');
      expect(model.graph.structuralHubs.items).toHaveLength(0);
    });
  });

  describe('Risk normalization', () => {
    it('preserves 47.58 MEDIUM', () => {
      const model = normalizeIntelligence(frozenBackendResponse);

      expect(model.risk.score).toBe(47.58);
      expect(model.risk.level).toBe('MEDIUM');
    });

    it('preserves legacy fields explicitly', () => {
      const model = normalizeIntelligence(frozenBackendResponse);

      expect(model.risk.anomaly_score).toBe(0.0);
      expect(model.risk.collusion_score).toBe(0.0);
      expect(model.risk.financial_score).toBe(0.0);
    });

    it('preserves recommendations array', () => {
      const model = normalizeIntelligence(frozenBackendResponse);

      expect(model.risk.recommendations).toHaveLength(3);
      expect(model.risk.recommendations[0]).toContain('Schedule follow-up review');
    });
  });

  describe('Evidence normalization', () => {
    it('availability = NO_DATA (evidence.total = 0)', () => {
      const model = normalizeIntelligence(frozenBackendResponse);

      expect(model.evidence.availability).toBe('NO_DATA');
      expect(model.evidence.total).toBe(0);
      expect(model.evidence.score).toBe(0.0);
      expect(model.evidence.level).toBe('NO_DATA');
    });
  });

  describe('Findings normalization', () => {
    it('preserves root aggregate counts (from data.total/critical/high/medium)', () => {
      const model = normalizeIntelligence(frozenBackendResponse);

      expect(model.findings.total).toBe(9);
      expect(model.findings.critical).toBe(0);
      expect(model.findings.high).toBe(2);
      expect(model.findings.medium).toBe(5);
    });

    it('items and findings alias point to same array (backward compat)', () => {
      const model = normalizeIntelligence(frozenBackendResponse);

      expect(model.findings.items).toBe(model.findings.findings);
    });

    it('items are normalized with metadata', () => {
      const model = normalizeIntelligence(frozenBackendResponse);

      expect(model.findings.items.length).toBe(2);
      expect(model.findings.items[0]).toHaveProperty('id');
      expect(model.findings.items[0]).toHaveProperty('source');
      expect(model.findings.items[0]).toHaveProperty('severity');
      expect(model.findings.items[0]).toHaveProperty('detectedAt');
    });
  });

  describe('Metadata normalization', () => {
    it('preserves generatedAt, requestId, traceId', () => {
      const model = normalizeIntelligence(frozenBackendResponse);

      expect(model.generatedAt).toBe('2026-09-22T02:09:53.806633Z');
      expect(model.requestId).toBe('test-request-id');
      expect(model.traceId).toBe('test-trace-id');
    });

    it('freshness derived from generated_at', () => {
      const model = normalizeIntelligence(frozenBackendResponse);

      expect(['FRESH', 'STALE', 'UNKNOWN']).toContain(model.freshness);
    });
  });

  describe('Null-safety', () => {
    it('returns safe empty model for null', () => {
      const model = normalizeIntelligence(null);

      expect(model.case_id).toBe('');
      expect(model.fraud.patterns).toHaveLength(0);
      expect(model.graph.entities).toBe(0);
      expect(model.risk.score).toBe(0);
      expect(model.findings.items).toHaveLength(0);
      expect(model.freshness).toBe('UNKNOWN');
    });

    it('returns safe empty model for undefined', () => {
      const model = normalizeIntelligence(undefined);

      expect(model.case_id).toBe('');
      expect(model.fraud.clustersAvailability).toBe('NOT_AVAILABLE');
      expect(model.graph.structuralHubs.availability).toBe('NOT_AVAILABLE');
    });
  });
});
