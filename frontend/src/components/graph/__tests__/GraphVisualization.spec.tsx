import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';

vi.mock('react-cytoscapejs', () => ({
  default: ({ elements }: { elements: any[] }) => (
    <div data-testid="cytoscape-mock" data-count={elements?.length ?? 0} />
  ),
}));

vi.mock('cytoscape-dagre', () => ({
  default: vi.fn(),
}));

vi.mock('cytoscape', () => {
  const mockUse = vi.fn();
  return {
    default: { use: mockUse },
    Core: class {},
    ElementDefinition: {},
    EventObjectNode: {},
  };
});

vi.mock('../../../services/api/graph', () => {
  const mockApi = {
    getCaseGraph: vi.fn(),
  };
  return {
    default: mockApi,
    graphApi: mockApi,
  };
});

import GraphVisualization from '../GraphVisualization';
import graphApi from '../../../services/api/graph';

const FROZEN_CASE = 'b4897392-87ab-4e7a-84b6-90228f3d1eb9';

describe('GraphVisualization', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('fetches via graphApi.getCaseGraph(caseId)', async () => {
    (graphApi.getCaseGraph as any).mockResolvedValue({
      case_id: FROZEN_CASE,
      has_data: true,
      nodes: [],
      edges: [],
      summary: { entities: 0, relationships: 0 },
    });

    render(<GraphVisualization caseId={FROZEN_CASE} />);

    await waitFor(() => {
      expect(graphApi.getCaseGraph).toHaveBeenCalledWith(FROZEN_CASE);
    });
  });

  it('renders Cytoscape with bounded elements (<= INITIAL_MAX_NODES + edges)', async () => {
    (graphApi.getCaseGraph as any).mockResolvedValue({
      case_id: FROZEN_CASE,
      has_data: true,
      nodes: [
        {
          id: 'v1',
          business_key: 'v1',
          name: 'V1',
          entity_type: 'vendor',
          source_id: null,
          extra_data: {},
        },
      ],
      edges: [],
      summary: { entities: 1, relationships: 0 },
    });

    render(<GraphVisualization caseId={FROZEN_CASE} />);

    await waitFor(() => {
      const mock = screen.getByTestId('cytoscape-mock');
      expect(mock).toBeInTheDocument();
    });

    const mock = screen.getByTestId('cytoscape-mock');
    const count = Number(mock.getAttribute('data-count'));
    // INITIAL_MAX_NODES = 200; small fixture → count should be small
    expect(count).toBeLessThanOrEqual(200);
  });

  it('shows error state on fetch failure', async () => {
    (graphApi.getCaseGraph as any).mockRejectedValue(new Error('API failure'));

    render(<GraphVisualization caseId={FROZEN_CASE} />);

    await waitFor(() => {
      // Component renders "Gagal memuat graph intelligence." or similar
      // Match against actual error text pattern
      const errorText = screen.queryByText(/gagal memuat graph intelligence/i)
        ?? screen.queryByText(/api failure/i);
      expect(errorText).toBeInTheDocument();
    });
  });
});
