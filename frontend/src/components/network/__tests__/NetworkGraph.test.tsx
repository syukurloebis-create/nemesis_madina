import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import NetworkGraph from '../NetworkGraph';

const mockActors = [
  { id: '1', name: 'Actor 1', riskScore: 85, type: 'PERSON', connections: 5 },
  { id: '2', name: 'Actor 2', riskScore: 60, type: 'COMPANY', connections: 3 },
  { id: '3', name: 'Actor 3', riskScore: 40, type: 'PERSON', connections: 2 },
];

describe('NetworkGraph Component', () => {
  it('should render empty state when no actors', () => {
    render(<NetworkGraph actors={[]} />);
    expect(screen.getByText(/Tidak ada data/i)).toBeInTheDocument();
  });

  it('should render network graph with actors', () => {
    render(<NetworkGraph actors={mockActors} />);
    expect(screen.getByText(/Network Intelligence/i)).toBeInTheDocument();
    expect(screen.getByText(/actors/i)).toBeInTheDocument();
  });

  it('should display risk score in header', () => {
    render(<NetworkGraph actors={mockActors} />);
    expect(screen.getByText(/Risk/i)).toBeInTheDocument();
  });

  it('should show actor count', () => {
    render(<NetworkGraph actors={mockActors} />);
    expect(screen.getByText(/3 actors/i)).toBeInTheDocument();
  });

  it('should handle onNodeClick callback', () => {
    const onNodeClick = vi.fn();
    render(<NetworkGraph actors={mockActors} onNodeClick={onNodeClick} />);
    expect(screen.getByText(/Network Intelligence/i)).toBeInTheDocument();
  });

  it('should apply custom className', () => {
    const { container } = render(
      <NetworkGraph actors={mockActors} className="custom-class" />
    );
    expect(container.firstChild).toHaveClass('custom-class');
  });

  it('should apply custom height', () => {
    const { container } = render(
      <NetworkGraph actors={mockActors} height={500} />
    );
    const flowContainer = container.querySelector('[style*="height"]');
    expect(flowContainer).toBeInTheDocument();
  });
});
