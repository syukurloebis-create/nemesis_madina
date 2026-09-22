import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';

// ─── Mock investigationService BEFORE importing component ────────
vi.mock('../../../services/investigations', () => ({
  investigationService: {
    getByCase: vi.fn(),
    getStats: vi.fn(),
    updateStatus: vi.fn(),
  },
}));

import InvestigationWorkspace from '../InvestigationWorkspace';
import { investigationService } from '../../../services/investigations';

const FROZEN_CASE = 'b4897392-87ab-4e7a-84b6-90228f3d1eb9';

describe('InvestigationWorkspace — Phase C.4', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders "No case selected" when caseId is undefined', () => {
    render(<InvestigationWorkspace />);
    expect(screen.getByText(/No case selected/i)).toBeInTheDocument();
  });

  it('fetches investigations via investigationService on caseId', async () => {
    (investigationService.getByCase as any).mockResolvedValue({
      data: [],
    });
    (investigationService.getStats as any).mockResolvedValue({
      data: { total: 0, active: 0, completed: 0, pending: 0 },
    });

    render(<InvestigationWorkspace caseId={FROZEN_CASE} />);

    await waitFor(() => {
      expect(investigationService.getByCase).toHaveBeenCalledWith(FROZEN_CASE);
      expect(investigationService.getStats).toHaveBeenCalledWith(FROZEN_CASE);
    });
  });

  it('renders explicit empty state with message', async () => {
    (investigationService.getByCase as any).mockResolvedValue({ data: [] });
    (investigationService.getStats as any).mockResolvedValue({
      data: { total: 0, active: 0, completed: 0, pending: 0 },
    });

    render(<InvestigationWorkspace caseId={FROZEN_CASE} />);

    await waitFor(() => {
      expect(
        screen.getByText(/No investigations have been created for this case/i),
      ).toBeInTheDocument();
    });
  });

  it('renders disabled Create Investigation CTA in empty state', async () => {
    (investigationService.getByCase as any).mockResolvedValue({ data: [] });
    (investigationService.getStats as any).mockResolvedValue({
      data: { total: 0, active: 0, completed: 0, pending: 0 },
    });

    render(<InvestigationWorkspace caseId={FROZEN_CASE} />);

    await waitFor(() => {
      const button = screen.getByRole('button', { name: /Create Investigation/i });
      expect(button).toBeInTheDocument();
      expect(button).toBeDisabled();
    });
  });

  it('renders honest "not yet available" note', async () => {
    (investigationService.getByCase as any).mockResolvedValue({ data: [] });
    (investigationService.getStats as any).mockResolvedValue({
      data: { total: 0, active: 0, completed: 0, pending: 0 },
    });

    render(<InvestigationWorkspace caseId={FROZEN_CASE} />);

    await waitFor(() => {
      expect(
        screen.getByText(/not yet available in this environment/i),
      ).toBeInTheDocument();
    });
  });

  it('renders investigations list when data is present', async () => {
    (investigationService.getByCase as any).mockResolvedValue({
      data: [
        {
          id: 'inv-1',
          case_id: FROZEN_CASE,
          title: 'Test Investigation',
          status: 'ACTIVE',
          priority: 'HIGH',
          created_at: '2026-09-22T00:00:00Z',
          updated_at: '2026-09-22T00:00:00Z',
        },
      ],
    });
    (investigationService.getStats as any).mockResolvedValue({
      data: { total: 1, active: 1, completed: 0, pending: 0 },
    });

    render(<InvestigationWorkspace caseId={FROZEN_CASE} />);

    await waitFor(() => {
      expect(screen.getByText('Test Investigation')).toBeInTheDocument();
    });

    // Empty CTA should NOT be rendered when list is non-empty
    expect(
      screen.queryByRole('button', { name: /Create Investigation/i }),
    ).not.toBeInTheDocument();
  });

  it('does not render legacy/fabricated fields in DOM', async () => {
    (investigationService.getByCase as any).mockResolvedValue({ data: [] });
    (investigationService.getStats as any).mockResolvedValue({
      data: { total: 0, active: 0, completed: 0, pending: 0 },
    });

    const { container } = render(<InvestigationWorkspace caseId={FROZEN_CASE} />);

    await waitFor(() => {
      expect(container.textContent ?? '').toMatch(/No investigations/i);
    });

    const text = container.textContent ?? '';
    expect(text).not.toMatch(/risk_score/);
    expect(text).not.toMatch(/riskScore/);
    expect(text).not.toMatch(/trustScore/);
  });
});
