import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import Dashboard from '../Dashboard';

describe('Dashboard Component', () => {
  it('should render dashboard correctly', () => {
    render(<Dashboard />);
    // Check if dashboard renders without errors
    expect(screen.getByText(/NEMESIS/i)).toBeInTheDocument();
  });
});
