import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';

// Mock useIntelligenceDashboard BEFORE importing component
vi.mock('../../hooks/useIntelligenceDashboard', () => ({
  useIntelligenceDashboard: vi.fn(),
}));

import RecoveryIntelligence from '../RecoveryIntelligence';
import { useIntelligenceDashboard } from '../../hooks/useIntelligenceDashboard';

const FROZEN_CASE = 'b4897392-87ab-4e7a-84b6-90228f3d1eb9';

describe('RecoveryIntelligence — Phase C.5', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders loading state initially', () => {
    (useIntelligenceDashboard as any).mockReturnValue({
      data: null,
      loading: true,
      error: null,
    });

    render(<RecoveryIntelligence />);
    expect(screen.getByText(/Loading recovery intelligence/i)).toBeInTheDocument();
  });

  it('renders error state on failure', () => {
    (useIntelligenceDashboard as any).mockReturnValue({
      data: null,
      loading: false,
      error: 'Network error',
    });

    render(<RecoveryIntelligence />);
    expect(screen.getByText(/Failed to load recovery intelligence/i)).toBeInTheDocument();
    expect(screen.getByText(/Network error/)).toBeInTheDocument();
  });

  it('renders no-data state when recovery is missing', () => {
    (useIntelligenceDashboard as any).mockReturnValue({
      data: {},
      loading: false,
      error: null,
    });

    render(<RecoveryIntelligence />);
    expect(screen.getByText(/No recovery data available/i)).toBeInTheDocument();
  });

  it('renders engine status in separate section', () => {
    (useIntelligenceDashboard as any).mockReturnValue({
      data: {
        recovery: {
          business_state: 'READY',
          actions: [],
          engine: 'recovery',
          engine_status: 'OK',
        },
      },
      loading: false,
      error: null,
    });

    render(<RecoveryIntelligence />);

    expect(screen.getByText('Recovery Engine')).toBeInTheDocument();
    expect(screen.getByText('● OK')).toBeInTheDocument();
    expect(screen.getByText('recovery')).toBeInTheDocument();
  });

  it('renders case recovery state in separate section', () => {
    (useIntelligenceDashboard as any).mockReturnValue({
      data: {
        recovery: {
          business_state: 'READY',
          actions: [],
          engine: 'recovery',
          engine_status: 'OK',
        },
      },
      loading: false,
      error: null,
    });

    render(<RecoveryIntelligence />);

    expect(screen.getByText('Case Recovery State')).toBeInTheDocument();
    expect(screen.getByText('READY')).toBeInTheDocument();
    expect(screen.getByText(/No recovery actions defined/i)).toBeInTheDocument();
  });

  it('renders actions list when present', () => {
    (useIntelligenceDashboard as any).mockReturnValue({
      data: {
        recovery: {
          business_state: 'ACTIVE',
          actions: [
            { id: 'a1', description: 'Recover asset A' },
            { id: 'a2', description: 'Recover asset B' },
          ],
          engine: 'recovery',
          engine_status: 'OK',
        },
      },
      loading: false,
      error: null,
    });

    render(<RecoveryIntelligence />);

    expect(screen.getByText(/2 actions defined/)).toBeInTheDocument();
    expect(screen.getByText('Recover asset A')).toBeInTheDocument();
    expect(screen.getByText('Recover asset B')).toBeInTheDocument();
  });

  it('uses FROZEN_CASE_ID fallback when caseId not provided', () => {
    (useIntelligenceDashboard as any).mockReturnValue({
      data: { recovery: { business_state: 'READY', actions: [], engine: 'recovery', engine_status: 'OK' } },
      loading: false,
      error: null,
    });

    render(<RecoveryIntelligence />);
    expect(useIntelligenceDashboard).toHaveBeenCalledWith(FROZEN_CASE);
  });

  it('uses provided caseId when passed', () => {
    const customCase = 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee';
    (useIntelligenceDashboard as any).mockReturnValue({
      data: { recovery: { business_state: 'READY', actions: [], engine: 'recovery', engine_status: 'OK' } },
      loading: false,
      error: null,
    });

    render(<RecoveryIntelligence caseId={customCase} />);
    expect(useIntelligenceDashboard).toHaveBeenCalledWith(customCase);
  });

  it('does not render forbidden fields in DOM', () => {
    (useIntelligenceDashboard as any).mockReturnValue({
      data: { recovery: { business_state: 'READY', actions: [], engine: 'recovery', engine_status: 'OK' } },
      loading: false,
      error: null,
    });

    const { container } = render(<RecoveryIntelligence />);
    const text = container.textContent ?? '';
    expect(text).not.toMatch(/risk_score/);
    expect(text).not.toMatch(/riskScore/);
    expect(text).not.toMatch(/trustScore/);
  });
});
