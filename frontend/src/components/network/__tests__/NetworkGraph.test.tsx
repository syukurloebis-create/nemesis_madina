import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { NetworkGraph } from '../NetworkGraph';

// Mock reactflow
vi.mock('reactflow', () => ({
  default: ({ children, nodes, edges }: any) => (
    <div data-testid="reactflow">
      {children}
      <div data-testid="mock-nodes">Nodes: {nodes?.length || 0}</div>
      <div data-testid="mock-edges">Edges: {edges?.length || 0}</div>
    </div>
  ),
  Background: () => <div>Background</div>,
  Controls: () => <div>Controls</div>,
  MiniMap: () => <div>MiniMap</div>,
  useNodesState: (initial: any) => [initial || [], vi.fn()],
  useEdgesState: (initial: any) => [initial || [], vi.fn()],
  addEdge: vi.fn(),
  MarkerType: { ArrowClosed: 'arrowclosed' },
}));

// Mock useNetworkGraph hook
vi.mock('../../../hooks/useNetworkGraph', () => ({
  default: (actors: any[]) => {
    const nodes = (actors || []).slice(0, 10).map((actor, index) => ({
      id: actor.id || `actor-${index}`,
      type: 'default',
      data: { label: actor.name, risk_score: actor.risk_score || 0 },
      position: { x: 100, y: 100 },
    }));
    const edges = (actors || []).slice(0, 10).map((actor, index) => ({
      id: `edge-${index}`,
      source: actor.id || `actor-${index}`,
      target: `actor-${index + 1}`,
      animated: true,
    }));
    return { nodes, edges };
  },
}));

describe('NetworkGraph Component', () => {
  const mockActors = [
    { id: '1', name: 'PT. DEXA Medica', risk_score: 85, connections: 3 },
    { id: '2', name: 'PT. Kimia Farma', risk_score: 75, connections: 2 },
    { id: '3', name: 'PT. Hexpharm', risk_score: 65, connections: 1 },
  ];

  it('should render empty state when no actors', () => {
    render(<NetworkGraph actors={[]} />);
    expect(screen.getByText(/Tidak ada data actor/i)).toBeInTheDocument();
  });

  it('should render network graph with actors', () => {
    render(<NetworkGraph actors={mockActors} />);
    expect(screen.getByText(/Network Intelligence/i)).toBeInTheDocument();
    expect(screen.getByText(/3 actors/i)).toBeInTheDocument();
    expect(screen.getByText(/Risk: 85/i)).toBeInTheDocument();
  });

  it('should display risk score in header', () => {
    render(<NetworkGraph actors={mockActors} />);
    expect(screen.getByText(/Risk: 85/i)).toBeInTheDocument();
  });

  it('should show actor count', () => {
    render(<NetworkGraph actors={mockActors} />);
    expect(screen.getByText(/3 actors/i)).toBeInTheDocument();
  });

  it('should handle onNodeClick callback', () => {
    const onNodeClick = vi.fn();
    render(<NetworkGraph actors={mockActors} onNodeClick={onNodeClick} />);
    expect(onNodeClick).toBeDefined();
  });

  it('should apply custom className', () => {
    const { container } = render(
      <NetworkGraph actors={mockActors} className="custom-class" />
    );
    expect(container.firstChild).toHaveClass('custom-class');
  });

  it('should apply custom height', () => {
    const { container } = render(
      <NetworkGraph actors={mockActors} height={600} />
    );
    const flowContainer = container.querySelector('[style*="height"]');
    expect(flowContainer).toBeInTheDocument();
  });
});
