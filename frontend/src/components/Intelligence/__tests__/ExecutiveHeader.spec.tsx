import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// ─── Mock riskApi BEFORE importing component ────────────────────────
vi.mock('../../../services/api/risk', () => ({
  riskApi: {
    getExplanations: vi.fn().mockResolvedValue(null),
  },
}));

import ExecutiveHeader from '../ExecutiveHeader';
import type { IntelligenceModel } from '../../../services/intelligenceAdapter';

const FROZEN_CASE = 'b4897392-87ab-4e7a-84b6-90228f3d1eb9';

/**
 * Build a minimal IntelligenceModel that satisfies the shape
 * accessed by ExecutiveHeader (case_id, risk, fraud, generatedAt,
 * freshness, requestId).
 */
function buildIntelligence(
  overrides: Partial<IntelligenceModel> = {},
): IntelligenceModel {
  const base: IntelligenceModel = {
    case_id: FROZEN_CASE,
    fraud: {
      overall_risk: 'HIGH',
      score: 75.27,
      active_alerts: 2,
      high_confidence: 2,
      total_patterns: 3,
      validated_patterns: 0,
      highest_confidence: 85.5,
      average_confidence: 75.27,
      patterns: [],
      clustersAvailability: 'NOT_AVAILABLE',
      engine: 'fraud',
      engine_status: 'OK',
    },
    risk: {
      score: 47.58,
      level: 'MEDIUM',
      anomaly_score: 0,
      collusion_score: 0,
      financial_score: 0,
      recommendations: [],
      engine: 'risk',
      engine_status: 'OK',
    },
    graph: {
      entities: 4177,
      relationships: 2424,
      structuralHubs: { availability: 'NOT_AVAILABLE', items: [] },
      engine: 'graph',
      engine_status: 'OK',
    },
    evidence: {
      score: 0,
      level: 'NO_DATA',
      total: 0,
      verified: 0,
      rejected: 0,
      pending: 0,
      avg_trust: 0,
      avg_confidence: 0,
      availability: 'NO_DATA',
      engine: 'evidence',
      engine_status: 'OK',
    },
    findings: {
      total: 9,
      critical: 0,
      high: 2,
      medium: 5,
      items: [],
      findings: [],
    },
    generatedAt: '2026-09-22T04:46:04.052430Z',
    requestId: 'b9bbe3be-43a4-49c3-98ad-dc0e9017b896',
    traceId: '4f9883b1-1902-46c0-bd72-bc0e0e674252',
    freshness: 'FRESH',
  };

  return { ...base, ...overrides };
}

function renderWithQuery(ui: React.ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>,
  );
}

describe('ExecutiveHeader — Phase C.1 metadata', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders "Last calculated" label', () => {
    renderWithQuery(<ExecutiveHeader intelligence={buildIntelligence()} />);
    expect(screen.getByText(/Last calculated:/)).toBeInTheDocument();
  });

  it('renders formatted timestamp when generatedAt present', () => {
    renderWithQuery(<ExecutiveHeader intelligence={buildIntelligence()} />);
    // Format: "Last calculated: 2026-09-22 04:46:04 UTC"
    expect(
      screen.getByText(/Last calculated: 2026-09-22 04:46:04 UTC/),
    ).toBeInTheDocument();
  });

  it('renders placeholder "—" when generatedAt is null', () => {
    renderWithQuery(
      <ExecutiveHeader
        intelligence={buildIntelligence({
          generatedAt: null,
          freshness: 'UNKNOWN',
        })}
      />,
    );
    expect(
      screen.getByText(/Last calculated: —/),
    ).toBeInTheDocument();
  });

  it('renders FRESH badge when freshness is FRESH', () => {
    renderWithQuery(<ExecutiveHeader intelligence={buildIntelligence()} />);
    expect(screen.getByText('Fresh')).toBeInTheDocument();
  });

  it('renders UNKNOWN badge when freshness is UNKNOWN', () => {
    renderWithQuery(
      <ExecutiveHeader
        intelligence={buildIntelligence({
          generatedAt: null,
          freshness: 'UNKNOWN',
        })}
      />,
    );
    expect(screen.getByText('Unknown')).toBeInTheDocument();
  });

  it('renders req ID prefix when requestId present', () => {
    renderWithQuery(<ExecutiveHeader intelligence={buildIntelligence()} />);
    expect(screen.getByText(/req: b9bbe3be/)).toBeInTheDocument();
  });

  it('does not render req segment when requestId is null', () => {
    renderWithQuery(
      <ExecutiveHeader
        intelligence={buildIntelligence({ requestId: null })}
      />,
    );
    expect(screen.queryByText(/req:/)).not.toBeInTheDocument();
  });

  it('does not render risk_score / riskScore / confidence text', () => {
    const { container } = renderWithQuery(
      <ExecutiveHeader intelligence={buildIntelligence()} />,
    );
    const text = container.textContent ?? '';
    expect(text).not.toMatch(/risk_score/);
    expect(text).not.toMatch(/riskScore/);
    expect(text).not.toMatch(/trustScore/);
  });
});
