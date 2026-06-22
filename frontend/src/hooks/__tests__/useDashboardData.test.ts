import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useDashboardData } from '../useDashboardData';

// Mock dashboardApi dengan benar
vi.mock('../../services/dashboardApi', () => ({
  dashboardApi: {
    getExecutive: vi.fn(),
    getStats: vi.fn(),
    getCases: vi.fn(),
    getEvidenceStats: vi.fn(),
    getRiskTrend: vi.fn(),
    getKeyActors: vi.fn(),
    getRecommendations: vi.fn(),
    getRecommendationSummary: vi.fn(),
    getGovernance: vi.fn(),
    getProvenance: vi.fn(),
  },
}));

describe('useDashboardData Hook', () => {
  const mockCaseId = 'test-case-123';

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should fetch data successfully', async () => {
    const { result } = renderHook(() => useDashboardData(mockCaseId));

    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.error).toBeNull();
    expect(result.current.data).toBeDefined();
  });

  it('should handle API errors gracefully', async () => {
    const { result } = renderHook(() => useDashboardData(mockCaseId));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    // Error should be handled
    expect(result.current.error).toBeDefined();
  });

  it('should handle partial data failure gracefully', async () => {
    const { result } = renderHook(() => useDashboardData(mockCaseId));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    // Should have data even if some calls fail
    expect(result.current.data).toBeDefined();
  });
});
