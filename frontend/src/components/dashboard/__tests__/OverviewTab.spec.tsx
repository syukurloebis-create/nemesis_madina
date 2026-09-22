import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';

import OverviewTab from '../OverviewTab';
import type { IntelligenceModel } from '../../../services/intelligenceAdapter';

const FROZEN_CASE = 'b4897392-87ab-4e7a-84b6-90228f3d1eb9';

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

describe('OverviewTab — Phase C.2 metadata', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders "Last calculated" label', () => {
    render(<OverviewTab intelligence={buildIntelligence()} />);
    expect(screen.getByText(/Last calculated:/)).toBeInTheDocument();
  });

  it('renders formatted timestamp when generatedAt present', () => {
    render(<OverviewTab intelligence={buildIntelligence()} />);
    expect(
      screen.getByText(/Last calculated: 2026-09-22 04:46:04 UTC/),
    ).toBeInTheDocument();
  });

  it('renders placeholder "—" when generatedAt is null', () => {
    render(
      <OverviewTab
        intelligence={buildIntelligence({
          generatedAt: null,
          freshness: 'UNKNOWN',
        })}
      />,
    );
    expect(screen.getByText(/Last calculated: —/)).toBeInTheDocument();
  });

  it('renders FRESH badge when freshness is FRESH', () => {
    render(<OverviewTab intelligence={buildIntelligence()} />);
    expect(screen.getByText('Fresh')).toBeInTheDocument();
  });

  it('renders UNKNOWN badge when freshness is UNKNOWN', () => {
    render(
      <OverviewTab
        intelligence={buildIntelligence({
          generatedAt: null,
          freshness: 'UNKNOWN',
        })}
      />,
    );
    expect(screen.getByText('Unknown')).toBeInTheDocument();
  });

  it('renders req ID prefix when requestId present', () => {
    render(<OverviewTab intelligence={buildIntelligence()} />);
    expect(screen.getByText(/req: b9bbe3be/)).toBeInTheDocument();
  });

  it('does not render req segment when requestId is null', () => {
    render(
      <OverviewTab
        intelligence={buildIntelligence({ requestId: null })}
      />,
    );
    expect(screen.queryByText(/req:/)).not.toBeInTheDocument();
  });

  it('does not render forbidden fields in DOM', () => {
    const { container } = render(
      <OverviewTab intelligence={buildIntelligence()} />,
    );
    const text = container.textContent ?? '';
    expect(text).not.toMatch(/risk_score/);
    expect(text).not.toMatch(/riskScore/);
    expect(text).not.toMatch(/trustScore/);
  });
});
