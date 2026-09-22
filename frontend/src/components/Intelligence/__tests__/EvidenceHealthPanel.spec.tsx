import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';

import EvidenceHealthPanel from '../EvidenceHealthPanel';
import type { IntelligenceModel } from '../../../services/intelligenceAdapter';

const FROZEN_CASE = 'b4897392-87ab-4e7a-84b6-90228f3d1eb9';

function buildIntelligence(
  evidenceOverrides: Partial<IntelligenceModel['evidence']> = {},
): IntelligenceModel {
  return {
    case_id: FROZEN_CASE,
    fraud: {
      overall_risk: 'HIGH', score: 75.27, active_alerts: 2, high_confidence: 2,
      total_patterns: 3, validated_patterns: 0, highest_confidence: 85.5,
      average_confidence: 75.27, patterns: [], clustersAvailability: 'NOT_AVAILABLE',
      engine: 'fraud', engine_status: 'OK',
    },
    risk: {
      score: 47.58, level: 'MEDIUM', anomaly_score: 0, collusion_score: 0,
      financial_score: 0, recommendations: [], engine: 'risk', engine_status: 'OK',
    },
    graph: {
      entities: 4177, relationships: 2424,
      structuralHubs: { availability: 'NOT_AVAILABLE', items: [] },
      engine: 'graph', engine_status: 'OK',
    },
    evidence: {
      score: 0, level: 'NO_DATA', total: 0, verified: 0, rejected: 0, pending: 0,
      avg_trust: 0, avg_confidence: 0, availability: 'NO_DATA',
      engine: 'evidence', engine_status: 'OK',
      ...evidenceOverrides,
    },
    findings: { total: 9, critical: 0, high: 2, medium: 5, items: [], findings: [] },
    generatedAt: '2026-09-22T04:46:04.052430Z',
    requestId: 'b9bbe3be-43a4-49c3-98ad-dc0e9017b896',
    traceId: '4f9883b1-1902-46c0-bd72-bc0e0e674252',
    freshness: 'FRESH',
  };
}

describe('EvidenceHealthPanel — Phase C.3', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders explicit NO_DATA state when availability is NO_DATA', () => {
    render(<EvidenceHealthPanel intelligence={buildIntelligence()} />);
    expect(screen.getByText(/No evidence has been registered/i)).toBeInTheDocument();
  });

  it('renders impact on risk in NO_DATA state', () => {
    render(
      <EvidenceHealthPanel
        intelligence={buildIntelligence({ score: 0.00, availability: 'NO_DATA' })}
      />,
    );
    expect(screen.getByText(/Impact on current risk: 0\.00/)).toBeInTheDocument();
  });

  it('renders Register Evidence CTA (disabled) in NO_DATA state', () => {
    render(<EvidenceHealthPanel intelligence={buildIntelligence()} />);
    const button = screen.getByRole('button', { name: /Register Evidence/i });
    expect(button).toBeInTheDocument();
    expect(button).toBeDisabled();
  });

  it('renders honest "not yet available" note', () => {
    render(<EvidenceHealthPanel intelligence={buildIntelligence()} />);
    expect(screen.getByText(/Not yet available in this environment/i)).toBeInTheDocument();
  });

  it('renders NOT_AVAILABLE state when availability is NOT_AVAILABLE', () => {
    render(
      <EvidenceHealthPanel
        intelligence={buildIntelligence({ availability: 'NOT_AVAILABLE' })}
      />,
    );
    expect(screen.getByText(/Evidence data is not available from the API/i)).toBeInTheDocument();
  });

  it('renders ERROR state when availability is ERROR', () => {
    render(
      <EvidenceHealthPanel
        intelligence={buildIntelligence({ availability: 'ERROR' })}
      />,
    );
    expect(screen.getByText(/Failed to load evidence data/i)).toBeInTheDocument();
  });

  it('renders AVAILABLE state with canonical fields when availability is AVAILABLE', () => {
    render(
      <EvidenceHealthPanel
        intelligence={buildIntelligence({
          availability: 'AVAILABLE',
          score: 85.5,
          level: 'HIGH',
          total: 10,
          verified: 8,
          rejected: 3,
          pending: 4,
          avg_trust: 0.92,
          avg_confidence: 0.88,
        })}
      />,
    );

    expect(screen.getByText('85.50')).toBeInTheDocument();
    expect(screen.getByText('HIGH')).toBeInTheDocument();
    expect(screen.getByText('10')).toBeInTheDocument();
    expect(screen.getByText('8')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument();
    expect(screen.getByText('4')).toBeInTheDocument();
    expect(screen.getByText('0.92')).toBeInTheDocument();
    expect(screen.getByText('0.88')).toBeInTheDocument();
  });

  it('does not render legacy fields (confidence_level, components, custody_events, recommendation)', () => {
    const { container } = render(
      <EvidenceHealthPanel
        intelligence={buildIntelligence({ availability: 'AVAILABLE' })}
      />,
    );
    const text = container.textContent ?? '';
    expect(text).not.toMatch(/confidence_level/);
    expect(text).not.toMatch(/custody_events/);
    expect(text).not.toMatch(/recommendation/);
    expect(text).not.toMatch(/Trust Component/);
    expect(text).not.toMatch(/Verification Component/);
  });
});
