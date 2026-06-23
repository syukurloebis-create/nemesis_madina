import { describe, it, expect, vi, beforeEach } from 'vitest';
import { dashboardService } from '@/services/dashboard';

// Mock API modules
vi.mock('@/services/api', () => ({
  casesApi: {
    getStats: vi.fn().mockResolvedValue({ data: { total_cases: 10 } }),
  },
  evidenceApi: {
    getStats: vi.fn().mockResolvedValue({ data: { total: 50 } }),
  },
  graphApi: {
    getMetrics: vi.fn().mockResolvedValue({ data: { nodes: 100 } }),
  },
  fraudApi: {
    getStats: vi.fn().mockResolvedValue({ data: { patterns: 5 } }),
  },
  riskApi: {
    getTrend: vi.fn().mockResolvedValue({ data: { score: 75 } }),
  },
  recommendationApi: {
    getSummary: vi.fn().mockResolvedValue({ data: { total: 3 } }),
  },
  procurementApi: {
    getRUPStats: vi.fn().mockResolvedValue({ data: { total_packages: 20 } }),
  },
}));

describe('Dashboard Service', () => {
  const mockCaseId = 'test-case-123';

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should fetch dashboard data successfully', async () => {
    const result = await dashboardService.getDashboardData(mockCaseId);
    
    expect(result).toBeDefined();
    expect(result.executive).toBeDefined();
    expect(result.executive.totalCases).toBe(10);
  });

  it('should handle API errors gracefully', async () => {
    const { casesApi } = await import('@/services/api');
    casesApi.getStats.mockRejectedValueOnce(new Error('API Error'));
    
    const result = await dashboardService.getDashboardData(mockCaseId);
    
    expect(result).toBeDefined();
    expect(result.executive.totalCases).toBe(0);
  });
});
