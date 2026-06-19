import { renderHook, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { useDashboardData } from '../useDashboardData';
import dashboardApi from '../../services/dashboardApi';

// Mock API
vi.mock('../../services/dashboardApi', () => ({
  default: {
    getExecutive: vi.fn(),
    getStats: vi.fn(),
    getCases: vi.fn(),
    getEvidenceStats: vi.fn(),
    getRiskTrend: vi.fn(),
    getGovernance: vi.fn(),
    getKeyActors: vi.fn(),
    getRecommendations: vi.fn(),
    getTopEvidence: vi.fn(),
    getRecommendationSummary: vi.fn(),
  },
}));

describe('useDashboardData Hook', () => {
  const mockCaseId = '446e216d-eb0e-487e-8e6b-ec943468ea20';

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should fetch data successfully', async () => {
    const mockData = {
      executive: { risk_level: { critical: 3 } },
      stats: { total_cases: 6 },
      cases: [],
      evidence: { total: 23 },
      riskTrend: [],
      governance: { spip_maturity: 82 },
      keyActors: { key_actors: [{ name: 'Actor 1' }] },
      recommendations: [],
      topEvidence: [],
      summary: { CRITICAL: 3 },
    };

    (dashboardApi.getExecutive as any).mockResolvedValue({ data: mockData.executive });
    (dashboardApi.getStats as any).mockResolvedValue({ data: mockData.stats });
    (dashboardApi.getCases as any).mockResolvedValue({ data: mockData.cases });
    (dashboardApi.getEvidenceStats as any).mockResolvedValue({ data: mockData.evidence });
    (dashboardApi.getRiskTrend as any).mockResolvedValue({ data: mockData.riskTrend });
    (dashboardApi.getGovernance as any).mockResolvedValue({ data: mockData.governance });
    (dashboardApi.getKeyActors as any).mockResolvedValue({ data: mockData.keyActors });
    (dashboardApi.getRecommendations as any).mockResolvedValue({ data: mockData.recommendations });
    (dashboardApi.getTopEvidence as any).mockResolvedValue({ data: mockData.topEvidence });
    (dashboardApi.getRecommendationSummary as any).mockResolvedValue({ data: mockData.summary });

    const { result } = renderHook(() => useDashboardData(mockCaseId));

    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.error).toBeNull();
    expect(result.current.data.executive).toEqual(mockData.executive);
    expect(result.current.data.evidence).toEqual(mockData.evidence);
  });

  it('should handle API errors gracefully', async () => {
    // Mock semua API calls to reject
    (dashboardApi.getExecutive as any).mockRejectedValue(new Error('API Error'));
    (dashboardApi.getStats as any).mockRejectedValue(new Error('API Error'));
    (dashboardApi.getCases as any).mockRejectedValue(new Error('API Error'));
    (dashboardApi.getEvidenceStats as any).mockRejectedValue(new Error('API Error'));
    (dashboardApi.getRiskTrend as any).mockRejectedValue(new Error('API Error'));
    (dashboardApi.getGovernance as any).mockRejectedValue(new Error('API Error'));
    (dashboardApi.getKeyActors as any).mockRejectedValue(new Error('API Error'));
    (dashboardApi.getRecommendations as any).mockRejectedValue(new Error('API Error'));
    (dashboardApi.getTopEvidence as any).mockRejectedValue(new Error('API Error'));
    (dashboardApi.getRecommendationSummary as any).mockRejectedValue(new Error('API Error'));

    const { result } = renderHook(() => useDashboardData(mockCaseId));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    // Should have error since critical data is missing
    expect(result.current.error).toBe('Gagal memuat data dashboard');
  });

  it('should handle partial data failure gracefully', async () => {
    // Mock some APIs to succeed, some to fail
    (dashboardApi.getExecutive as any).mockResolvedValue({ data: { risk_level: { critical: 3 } } });
    (dashboardApi.getStats as any).mockRejectedValue(new Error('Stats error'));
    (dashboardApi.getCases as any).mockResolvedValue({ data: [] });
    (dashboardApi.getEvidenceStats as any).mockResolvedValue({ data: { total: 23 } });
    (dashboardApi.getRiskTrend as any).mockResolvedValue({ data: [] });
    (dashboardApi.getGovernance as any).mockResolvedValue({ data: null });
    (dashboardApi.getKeyActors as any).mockResolvedValue({ data: { key_actors: [] } });
    (dashboardApi.getRecommendations as any).mockResolvedValue({ data: [] });
    (dashboardApi.getTopEvidence as any).mockResolvedValue({ data: [] });
    (dashboardApi.getRecommendationSummary as any).mockResolvedValue({ data: null });

    const { result } = renderHook(() => useDashboardData(mockCaseId));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    // Should have data from successful calls and no error (critical data exists)
    expect(result.current.data.executive).toBeDefined();
    expect(result.current.data.evidence).toBeDefined();
    expect(result.current.error).toBeNull();
  });
});
