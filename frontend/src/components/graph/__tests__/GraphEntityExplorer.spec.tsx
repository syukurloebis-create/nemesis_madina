import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { GraphEntityExplorer } from '../GraphEntityExplorer';
import graphApi from '../../../services/api/graph';

vi.mock('../../../services/api/graph', () => {
  const mockApi = {
    getKeyActors: vi.fn(),
  };
  return {
    default: mockApi,
    graphApi: mockApi,
  };
});

const FROZEN_CASE = 'b4897392-87ab-4e7a-84b6-90228f3d1eb9';

describe('GraphEntityExplorer', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('calls graphApi.getKeyActors with (caseId, limit) when limit provided', async () => {
    (graphApi.getKeyActors as any).mockResolvedValue({
      case_id: FROZEN_CASE,
      actors: [],
      count: 0,
    });

    render(<GraphEntityExplorer caseId={FROZEN_CASE} limit={25} />);

    await waitFor(() => {
      expect(graphApi.getKeyActors).toHaveBeenCalledWith(FROZEN_CASE, 25);
    });
  });

  it('uses default limit 25 when not provided', async () => {
    (graphApi.getKeyActors as any).mockResolvedValue({
      case_id: FROZEN_CASE,
      actors: [],
      count: 0,
    });

    render(<GraphEntityExplorer caseId={FROZEN_CASE} />);

    await waitFor(() => {
      expect(graphApi.getKeyActors).toHaveBeenCalledWith(FROZEN_CASE, 25);
    });
  });

  it('renders actors in deterministic order: entity_type ASC > degree DESC > name ASC > business_key ASC', async () => {
    (graphApi.getKeyActors as any).mockResolvedValue({
      case_id: FROZEN_CASE,
      actors: [
        { id: 'b', business_key: 'b', name: 'Beta', entity_type: 'vendor', degree: 10 },
        { id: 'a', business_key: 'a', name: 'Alpha', entity_type: 'vendor', degree: 50 },
        { id: 'c', business_key: 'c', name: 'Charlie', entity_type: 'vendor', degree: 50 },
        { id: 'p1', business_key: 'p1', name: 'Proc1', entity_type: 'procurement_record', degree: 100 },
      ],
      count: 4,
    });

    render(<GraphEntityExplorer caseId={FROZEN_CASE} />);

    await waitFor(() => {
      expect(screen.getByText('Alpha')).toBeInTheDocument();
    });

    const buttons = screen.getAllByRole('button');
    const names = buttons
      .map((b) => {
        const nameEl = b.querySelector('.truncate');
        return nameEl?.textContent?.trim() ?? '';
      })
      .filter((n) => n.length > 0 && n !== 'Structural Hubs');

    // Expected order:
    // 1. Alpha   (vendor, degree 50, name A)
    // 2. Charlie (vendor, degree 50, name C)
    // 3. Beta    (vendor, degree 10)
    // 4. Proc1   (procurement_record)
    expect(names).toEqual(['Proc1', 'Alpha', 'Charlie', 'Beta']);
  });

  it('renders actor with canonical fields (name, entity_type, business_key, degree)', async () => {
    (graphApi.getKeyActors as any).mockResolvedValue({
      case_id: FROZEN_CASE,
      actors: [
        {
          id: 'x',
          business_key: 'cv.example',
          name: 'CV. Example',
          entity_type: 'vendor',
          degree: 42,
        },
      ],
      count: 1,
    });

    render(<GraphEntityExplorer caseId={FROZEN_CASE} />);

    await waitFor(() => {
      expect(screen.getByText('CV. Example')).toBeInTheDocument();
    });
    expect(screen.getByText('vendor')).toBeInTheDocument();
    expect(screen.getByText('cv.example')).toBeInTheDocument();
    expect(screen.getByText('42')).toBeInTheDocument();
  });

  it('filters actors by search query (case-insensitive)', async () => {
    (graphApi.getKeyActors as any).mockResolvedValue({
      case_id: FROZEN_CASE,
      actors: [
        { id: '1', business_key: 'p.t. dexa', name: 'P.T. Dexa', entity_type: 'vendor', degree: 50 },
        { id: '2', business_key: 'cv.aulia', name: 'CV. Aulia', entity_type: 'vendor', degree: 40 },
      ],
      count: 2,
    });

    render(<GraphEntityExplorer caseId={FROZEN_CASE} />);

    await waitFor(() => {
      expect(screen.getByText('P.T. Dexa')).toBeInTheDocument();
    });

    fireEvent.change(screen.getByPlaceholderText(/search/i), {
      target: { value: 'AULIA' },
    });

    expect(screen.getByText('CV. Aulia')).toBeInTheDocument();
    expect(screen.queryByText('P.T. Dexa')).not.toBeInTheDocument();
  });

  it('calls onNodeSelect with business_key on click', async () => {
    const onNodeSelect = vi.fn();
    (graphApi.getKeyActors as any).mockResolvedValue({
      case_id: FROZEN_CASE,
      actors: [
        { id: 'x', business_key: 'cv.example', name: 'CV. Example', entity_type: 'vendor', degree: 42 },
      ],
      count: 1,
    });

    render(<GraphEntityExplorer caseId={FROZEN_CASE} onNodeSelect={onNodeSelect} />);

    await waitFor(() => {
      expect(screen.getByText('CV. Example')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('CV. Example'));
    expect(onNodeSelect).toHaveBeenCalledWith('cv.example');
  });

  it('shows explicit empty state when no actors returned', async () => {
    (graphApi.getKeyActors as any).mockResolvedValue({
      case_id: FROZEN_CASE,
      actors: [],
      count: 0,
    });

    render(<GraphEntityExplorer caseId={FROZEN_CASE} />);

    await waitFor(() => {
      expect(
        screen.getByText(/tidak ada key actor yang dikembalikan/i),
      ).toBeInTheDocument();
    });
  });

  it('shows error state on fetch failure', async () => {
    (graphApi.getKeyActors as any).mockRejectedValue(new Error('Network error'));

    render(<GraphEntityExplorer caseId={FROZEN_CASE} />);

    await waitFor(() => {
      expect(screen.getByText(/network error/i)).toBeInTheDocument();
    });
  });
});
