import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';

vi.mock('react-cytoscapejs', () => ({
  default: ({ elements }: { elements: any[] }) => (
    <div data-testid="cytoscape-mock" data-count={elements?.length ?? 0} />
  ),
}));

vi.mock('cytoscape', () => ({
  default: { use: vi.fn() },
}));

vi.mock('../../../services/api/graph', () => {
  const mockApi = {
    getCollusion: vi.fn(),
    getCaseGraph: vi.fn(),
  };
  return {
    default: mockApi,
    graphApi: mockApi,
  };
});

import { CollusionGraphVisualization } from '../CollusionGraphVisualization';
import graphApi from '../../../services/api/graph';

const FROZEN_CASE = 'b4897392-87ab-4e7a-84b6-90228f3d1eb9';

const emptyPayload = {
  case_id: FROZEN_CASE,
  has_data: true,
  nodes: [],
  edges: [],
  summary: { entities: 0, relationships: 0 },
};

const emptyCollusion = {
  case_id: FROZEN_CASE,
  collusion_relationships: [],
  collusion_relationship_count: 0,
  detection_backed: false,
};

describe('CollusionGraphVisualization', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('fetches via graphApi.getCollusion + graphApi.getCaseGraph', async () => {
    (graphApi.getCollusion as any).mockResolvedValue(emptyCollusion);
    (graphApi.getCaseGraph as any).mockResolvedValue(emptyPayload);

    render(<CollusionGraphVisualization caseId={FROZEN_CASE} />);

    await waitFor(() => {
      expect(graphApi.getCollusion).toHaveBeenCalledWith(FROZEN_CASE);
      expect(graphApi.getCaseGraph).toHaveBeenCalledWith(FROZEN_CASE);
    });
  });

  it('shows explicit empty state when no collusion relationships', async () => {
    (graphApi.getCollusion as any).mockResolvedValue(emptyCollusion);
    (graphApi.getCaseGraph as any).mockResolvedValue(emptyPayload);

    render(<CollusionGraphVisualization caseId={FROZEN_CASE} />);

    await waitFor(() => {
      expect(
        screen.getByText(/tidak ada pola kolusi terdeteksi/i),
      ).toBeInTheDocument();
    });
  });

  it('builds nodes only from canonical source/target business_key', async () => {
    (graphApi.getCollusion as any).mockResolvedValue({
      case_id: FROZEN_CASE,
      collusion_relationships: [
        {
          id: null,
          source: 'cv.a',
          target: 'cv.b',
          relationship_type: 'COLLUSION',
          weight: 0.3,
          amount: null,
          description: null,
          extra_data: { shared_packages: 2 },
        },
      ],
      collusion_relationship_count: 1,
      detection_backed: false,
    });
    (graphApi.getCaseGraph as any).mockResolvedValue({
      case_id: FROZEN_CASE,
      has_data: true,
      nodes: [
        { id: 'cv.a', business_key: 'cv.a', name: 'CV. A', entity_type: 'vendor', source_id: null, extra_data: {} },
        { id: 'cv.b', business_key: 'cv.b', name: 'CV. B', entity_type: 'vendor', source_id: null, extra_data: {} },
        { id: 'cv.c', business_key: 'cv.c', name: 'CV. C', entity_type: 'vendor', source_id: null, extra_data: {} },
      ],
      edges: [],
      summary: { entities: 3, relationships: 0 },
    });

    render(<CollusionGraphVisualization caseId={FROZEN_CASE} />);

    await waitFor(() => {
      const mock = screen.getByTestId('cytoscape-mock');
      // 2 nodes (cv.a, cv.b) + 1 edge = 3 elements
      expect(Number(mock.getAttribute('data-count'))).toBe(3);
    });

    // Header should show "2 entitas · 1 hubungan COLLUSION"
    expect(screen.getByText(/2 entitas/i)).toBeInTheDocument();
  });

  it('renders only COLLUSION relationship_type edges', async () => {
    (graphApi.getCollusion as any).mockResolvedValue({
      case_id: FROZEN_CASE,
      collusion_relationships: [
        {
          id: null,
          source: 'cv.a',
          target: 'cv.b',
          relationship_type: 'COLLUSION',
          weight: 0.3,
          amount: null,
          description: null,
          extra_data: {},
        },
      ],
      collusion_relationship_count: 1,
      detection_backed: false,
    });
    (graphApi.getCaseGraph as any).mockResolvedValue({
      case_id: FROZEN_CASE,
      has_data: true,
      nodes: [
        { id: 'cv.a', business_key: 'cv.a', name: 'CV. A', entity_type: 'vendor', source_id: null, extra_data: {} },
        { id: 'cv.b', business_key: 'cv.b', name: 'CV. B', entity_type: 'vendor', source_id: null, extra_data: {} },
      ],
      edges: [
        { id: 'e1', source: 'cv.a', target: 'cv.b', relationship_type: 'VENDOR_HAS_PACKAGE', weight: 1, amount: null, description: null, extra_data: {} },
      ],
      summary: { entities: 2, relationships: 1 },
    });

    render(<CollusionGraphVisualization caseId={FROZEN_CASE} />);

    await waitFor(() => {
      // Wait for Cytoscape mock to render (state resolved)
      expect(screen.getByTestId('cytoscape-mock')).toBeInTheDocument();
    });

    // Header text may span multiple nodes — assert on body textContent
    const bodyText = document.body.textContent ?? '';
    expect(bodyText).toMatch(/1\s+hubungan\s+COLLUSION/i);
    // Ensure VENDOR_HAS_PACKAGE edge is NOT counted
    expect(bodyText).not.toMatch(/VENDOR_HAS_PACKAGE.*hubungan/i);
  });

  it('omits shared_packages label when not present in extra_data', async () => {
    (graphApi.getCollusion as any).mockResolvedValue({
      case_id: FROZEN_CASE,
      collusion_relationships: [
        {
          id: null,
          source: 'cv.a',
          target: 'cv.b',
          relationship_type: 'COLLUSION',
          weight: 0.3,
          amount: null,
          description: null,
          extra_data: {},
        },
      ],
      collusion_relationship_count: 1,
      detection_backed: false,
    });
    (graphApi.getCaseGraph as any).mockResolvedValue({
      case_id: FROZEN_CASE,
      has_data: true,
      nodes: [
        { id: 'cv.a', business_key: 'cv.a', name: 'CV. A', entity_type: 'vendor', source_id: null, extra_data: {} },
        { id: 'cv.b', business_key: 'cv.b', name: 'CV. B', entity_type: 'vendor', source_id: null, extra_data: {} },
      ],
      edges: [],
      summary: { entities: 2, relationships: 0 },
    });

    render(<CollusionGraphVisualization caseId={FROZEN_CASE} />);

    await waitFor(() => {
      expect(screen.getByTestId('cytoscape-mock')).toBeInTheDocument();
    });

    // No "shared" text should be rendered when shared_packages is absent
    expect(screen.queryByText(/shared/i)).not.toBeInTheDocument();
  });

  it('shows error state on fetch failure', async () => {
    (graphApi.getCollusion as any).mockRejectedValue(new Error('Fetch failed'));
    (graphApi.getCaseGraph as any).mockRejectedValue(new Error('Fetch failed'));

    render(<CollusionGraphVisualization caseId={FROZEN_CASE} />);

    await waitFor(() => {
      expect(screen.getByText(/fetch failed/i)).toBeInTheDocument();
    });
  });
});
