import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useDashboardData } from '../useDashboardData';

// Mock dashboard service
vi.mock('@/services', () => ({
  dashboardService: {
    getDashboardData: vi.fn(),
  },
}));

describe('useDashboardData Hook', () => {
  const mockCaseId = 'test-case-123';

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should fetch data successfully', async () => {
    const { dashboardService } = await import('@/services');
    const mockData = {
      executive: { totalCases: 10 },
      cases: [],
      evidence: {},
      graph: {},
      fraud: {},
      rup: {},
      stats: {},
      risk: {},
      recommendations: [],
      systemStatus: { isOnline: true },
    };
    
    dashboardService.getDashboardData.mockResolvedValue(mockData);

    const { result } = renderHook(() => useDashboardData(mockCaseId));

    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.error).toBeNull();
    expect(result.current.data).toEqual(mockData);
  });

  it('should handle API errors gracefully', async () => {
    const { dashboardService } = await import('@/services');
    dashboardService.getDashboardData.mockRejectedValue(new Error('Network error'));

    const { result } = renderHook(() => useDashboardData(mockCaseId));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.error).toBe('Network error');
    expect(result.current.data).toBeNull();
  });
});
