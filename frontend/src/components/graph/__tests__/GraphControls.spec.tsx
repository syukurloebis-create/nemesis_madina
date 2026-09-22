import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import GraphControls from '../GraphControls';

function buildDefaultProps(
  overrides: Partial<React.ComponentProps<typeof GraphControls>> = {},
): React.ComponentProps<typeof GraphControls> {
  return {
    entityTypes: [],
    relationshipTypes: [],
    availableEntityTypes: ['vendor', 'procurement_record'],
    availableRelationshipTypes: ['VENDOR_HAS_PACKAGE', 'COLLUSION'],
    layout: 'dagre',
    search: '',
    showAll: false,
    nodeCount: 0,
    totalNodeCount: 0,
    onEntityTypesChange: vi.fn(),
    onRelationshipTypesChange: vi.fn(),
    onLayoutChange: vi.fn(),
    onSearchChange: vi.fn(),
    onShowAllChange: vi.fn(),
    onZoomIn: vi.fn(),
    onZoomOut: vi.fn(),
    onFit: vi.fn(),
    onReset: vi.fn(),
    ...overrides,
  };
}

describe('GraphControls', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders entity type buttons with formatted labels', () => {
    render(<GraphControls {...buildDefaultProps()} />);
    expect(screen.getByText('Vendor')).toBeInTheDocument();
    expect(screen.getByText('Procurement Record')).toBeInTheDocument();
  });

  it('renders relationship type buttons with formatted labels', () => {
    render(<GraphControls {...buildDefaultProps()} />);
    expect(screen.getByText('Vendor → Package')).toBeInTheDocument();
    expect(screen.getByText('Collusion')).toBeInTheDocument();
  });

  it('calls onEntityTypesChange with added type on click (not previously selected)', () => {
    const onEntityTypesChange = vi.fn();
    render(<GraphControls {...buildDefaultProps({ onEntityTypesChange })} />);

    fireEvent.click(screen.getByText('Vendor'));
    expect(onEntityTypesChange).toHaveBeenCalledWith(['vendor']);
  });

  it('calls onEntityTypesChange with removed type on click (already selected)', () => {
    const onEntityTypesChange = vi.fn();
    render(
      <GraphControls
        {...buildDefaultProps({ entityTypes: ['vendor'], onEntityTypesChange })}
      />,
    );

    fireEvent.click(screen.getByText('Vendor'));
    expect(onEntityTypesChange).toHaveBeenCalledWith([]);
  });

  it('calls onSearchChange with typed value', () => {
    const onSearchChange = vi.fn();
    render(<GraphControls {...buildDefaultProps({ onSearchChange })} />);

    fireEvent.change(screen.getByLabelText('Cari node graph'), {
      target: { value: 'vendor' },
    });
    expect(onSearchChange).toHaveBeenCalledWith('vendor');
  });

  it('calls onLayoutChange with selected layout', () => {
    const onLayoutChange = vi.fn();
    render(<GraphControls {...buildDefaultProps({ onLayoutChange })} />);

    fireEvent.change(screen.getByLabelText('Layout graph'), {
      target: { value: 'circle' },
    });
    expect(onLayoutChange).toHaveBeenCalledWith('circle');
  });

  it('displays node count ratio', () => {
    render(
      <GraphControls
        {...buildDefaultProps({ nodeCount: 200, totalNodeCount: 4177 })}
      />,
    );
    expect(screen.getByText('200/4177')).toBeInTheDocument();
  });
});
