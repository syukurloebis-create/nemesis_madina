import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import Dashboard from '../Dashboard';

describe('Dashboard Component', () => {
  it('should render dashboard with correct text', () => {
    render(<Dashboard />);
    expect(screen.getByText('NEMESIS V8+ Test')).toBeInTheDocument();
    expect(screen.getByText('Dashboard working!')).toBeInTheDocument();
  });
});
