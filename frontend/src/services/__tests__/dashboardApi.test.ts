import { describe, it, expect, vi } from 'vitest';
import { dashboardApi } from '../dashboardApi';
import { api } from '../api';

vi.mock('../api', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

describe('dashboardApi Service', () => {
  it('should call getExecutive correctly', () => {
    dashboardApi.getExecutive();
    expect(api.get).toHaveBeenCalledWith('/api/v1/dashboard/executive/overview');
  });

  it('should call getStats correctly', () => {
    dashboardApi.getStats();
    expect(api.get).toHaveBeenCalledWith('/api/v1/investigation/stats');
  });

  it('should call getCases correctly', () => {
    dashboardApi.getCases();
    expect(api.get).toHaveBeenCalledWith('/api/v1/investigation/cases');
  });

  it('should call getEvidenceStats correctly', () => {
    dashboardApi.getEvidenceStats();
    expect(api.get).toHaveBeenCalledWith('/api/v1/evidence/stats');
  });

  it('should call getRiskTrend with default days', () => {
    dashboardApi.getRiskTrend();
    expect(api.get).toHaveBeenCalledWith('/api/v1/investigation/risk-trend?days=30');
  });

  it('should call getRiskTrend with custom days', () => {
    dashboardApi.getRiskTrend(60);
    expect(api.get).toHaveBeenCalledWith('/api/v1/investigation/risk-trend?days=60');
  });

  it('should call getKeyActors correctly', () => {
    dashboardApi.getKeyActors();
    expect(api.get).toHaveBeenCalledWith('/api/v1/graph/key-actors');
  });

  it('should call getRecommendations correctly', () => {
    dashboardApi.getRecommendations();
    expect(api.get).toHaveBeenCalledWith('/api/v1/recommendations/');
  });

  it('should call getRecommendationSummary correctly', () => {
    dashboardApi.getRecommendationSummary();
    expect(api.get).toHaveBeenCalledWith('/api/v1/recommendations/summary');
  });

  it('should call getGovernance correctly', () => {
    dashboardApi.getGovernance();
    expect(api.get).toHaveBeenCalledWith('/api/v1/dashboard/api/governance');
  });

  it('should call getProvenance with caseId', () => {
    const caseId = 'test-123';
    dashboardApi.getProvenance(caseId);
    expect(api.get).toHaveBeenCalledWith(`/api/v1/provenance/case/${caseId}`);
  });
});
