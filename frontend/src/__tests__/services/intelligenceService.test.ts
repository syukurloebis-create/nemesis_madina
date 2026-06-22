// frontend/src/__tests__/services/intelligenceService.test.ts
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { intelligenceService } from '@/services/intelligenceService';
import { api } from '@/services/api';

// Mock API
vi.mock('@/services/api', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

describe('IntelligenceService', () => {
  const mockCaseId = 'test-case-123';
  const mockKeyActors = [
    {
      id: 'actor-1',
      name: 'John Doe',
      type: 'PERSON',
      influence_score: 85,
      centrality: 0.9,
      connections: 45,
      risk_score: 75,
      collusion_risk: 0.7,
    },
    {
      id: 'actor-2',
      name: 'PT Maju Jaya',
      type: 'COMPANY',
      influence_score: 65,
      centrality: 0.6,
      connections: 30,
      risk_score: 55,
      collusion_risk: 0.4,
    },
  ];

  const mockCommunities = [
    {
      id: 'comm-1',
      members: ['actor-1', 'actor-2', 'actor-3'],
      density: 0.8,
      risk_score: 70,
      suspiciousness: 0.75,
    },
  ];

  const mockRiskData = {
    score: 72,
    factors: [
      {
        id: 'risk-1',
        category: 'FINANCIAL',
        description: 'Suspicious transactions detected',
        weight: 0.3,
        score: 80,
        evidence: ['tx-1', 'tx-2'],
        confidence: 0.85,
      },
    ],
    explanations: ['High financial risk due to irregular transactions'],
  };

  const mockFraudData = {
    patterns: [
      {
        id: 'fraud-1',
        type: 'COLLUSION',
        description: 'Bid rigging pattern detected',
        confidence: 0.82,
        entities: ['actor-1', 'actor-2'],
        evidence: ['doc-1', 'doc-2'],
      },
    ],
    signals: [
      {
        id: 'signal-1',
        type: 'PRICE_FIXING',
        source: 'ANALYTICS',
        confidence: 0.75,
        details: { price_variance: 0.3 },
      },
    ],
  };

  const mockReasoningData = {
    logs: [
      {
        rule_name: 'FraudDetection',
        input: { transaction: 1000000 },
        output: { risk_score: 80, fraud_probability: 0.75 },
        confidence: 0.8,
      },
    ],
    rules: [
      {
        id: 'rule-1',
        name: 'Transaction Monitoring',
        description: 'Monitors unusual transactions',
        weight: 0.5,
      },
    ],
  };

  beforeEach(() => {
    vi.clearAllMocks();
    
    // Mock API responses
    (api.get as any).mockImplementation((url: string, params?: any) => {
      if (url.includes('/graph/key-actors')) {
        return Promise.resolve({ data: mockKeyActors });
      }
      if (url.includes('/graph/communities')) {
        return Promise.resolve({ data: mockCommunities });
      }
      if (url.includes('/clusters/')) {
        return Promise.resolve({ data: [] });
      }
      if (url.includes('/graph/metrics')) {
        return Promise.resolve({ 
          data: { 
            nodes: 50, 
            edges: 120, 
            density: 0.3, 
            modularity: 0.6,
            avg_degree: 4.8,
            diameter: 8,
          } 
        });
      }
      if (url.includes('/risk-explanations')) {
        return Promise.resolve({ data: mockRiskData });
      }
      if (url.includes('/risk/scores')) {
        return Promise.resolve({ data: { scores: [mockRiskData] } });
      }
      if (url.includes('/risk/historical')) {
        return Promise.resolve({ 
          data: [
            { date: '2026-06-01', score: 60, level: 'MEDIUM', event: 'Initial assessment' },
            { date: '2026-06-15', score: 72, level: 'HIGH', event: 'New evidence found' },
          ] 
        });
      }
      if (url.includes('/fraud/patterns')) {
        return Promise.resolve({ data: mockFraudData.patterns });
      }
      if (url.includes('/fraud/signals')) {
        return Promise.resolve({ data: mockFraudData.signals });
      }
      if (url.includes('/reasoning/logs')) {
        return Promise.resolve({ data: mockReasoningData.logs });
      }
      if (url.includes('/reasoning/rules')) {
        return Promise.resolve({ data: mockReasoningData.rules });
      }
      return Promise.resolve({ data: {} });
    });
  });

  describe('getUnifiedIntelligence', () => {
    it('should fetch and aggregate intelligence data successfully', async () => {
      const result = await intelligenceService.getUnifiedIntelligence(mockCaseId);

      expect(result).toBeDefined();
      expect(result.caseId).toBe(mockCaseId);
      expect(result.metrics).toBeDefined();
      expect(result.graph).toBeDefined();
      expect(result.risk).toBeDefined();
      expect(result.fraud).toBeDefined();
      expect(result.reasoning).toBeDefined();
      
      // Check graph data
      expect(result.graph.keyActors).toHaveLength(2);
      expect(result.graph.keyActors[0].name).toBe('John Doe');
      expect(result.graph.communities).toHaveLength(1);
      expect(result.graph.metrics.nodes).toBe(50);
      
      // Check risk data
      expect(result.risk.score).toBe(72);
      expect(result.risk.level).toBe('HIGH');
      expect(result.risk.factors).toHaveLength(1);
      
      // Check fraud data
      expect(result.fraud.patterns).toHaveLength(1);
      expect(result.fraud.confidence).toBeGreaterThan(0);
      
      // Check reasoning
      expect(result.reasoning.recommendations).toBeDefined();
      expect(result.reasoning.confidence).toBeGreaterThan(0);
    });

    it('should handle API errors gracefully', async () => {
      (api.get as any).mockRejectedValueOnce(new Error('Network error'));
      
      await expect(intelligenceService.getUnifiedIntelligence(mockCaseId))
        .rejects
        .toThrow('Network error');
    });

    it('should cache intelligence data', async () => {
      // First call
      await intelligenceService.getUnifiedIntelligence(mockCaseId);
      const initialCallCount = (api.get as any).mock.calls.length;
      
      // Second call (should use cache)
      await intelligenceService.getUnifiedIntelligence(mockCaseId);
      const secondCallCount = (api.get as any).mock.calls.length;
      
      // Should not make additional API calls if cached
      expect(secondCallCount - initialCallCount).toBe(0);
    });

    it('should calculate correct overall score', async () => {
      const result = await intelligenceService.getUnifiedIntelligence(mockCaseId);
      
      expect(result.metrics.overallScore).toBeGreaterThan(0);
      expect(result.metrics.overallScore).toBeLessThanOrEqual(100);
      expect(result.metrics.investigationPriority).toBeDefined();
    });

    it('should transform key actors correctly', async () => {
      const result = await intelligenceService.getUnifiedIntelligence(mockCaseId);
      const actor = result.graph.keyActors[0];
      
      expect(actor).toHaveProperty('id');
      expect(actor).toHaveProperty('name');
      expect(actor).toHaveProperty('type');
      expect(actor).toHaveProperty('influence');
      expect(actor).toHaveProperty('centrality');
      expect(actor).toHaveProperty('connections');
      expect(actor).toHaveProperty('riskScore');
      expect(actor).toHaveProperty('collusionRisk');
      expect(actor).toHaveProperty('role');
    });

    it('should determine correct risk level', async () => {
      const result = await intelligenceService.getUnifiedIntelligence(mockCaseId);
      
      expect(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']).toContain(result.risk.level);
      expect(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']).toContain(result.metrics.investigationPriority);
    });

    it('should generate recommendations based on reasoning', async () => {
      const result = await intelligenceService.getUnifiedIntelligence(mockCaseId);
      
      expect(result.reasoning.recommendations.length).toBeGreaterThan(0);
      expect(result.reasoning.recommendations[0]).toHaveProperty('title');
      expect(result.reasoning.recommendations[0]).toHaveProperty('description');
      expect(result.reasoning.recommendations[0]).toHaveProperty('priority');
      expect(result.reasoning.recommendations[0]).toHaveProperty('confidence');
      expect(result.reasoning.recommendations[0]).toHaveProperty('actions');
    });

    it('should handle empty data gracefully', async () => {
      (api.get as any).mockImplementation(() => Promise.resolve({ data: null }));
      
      const result = await intelligenceService.getUnifiedIntelligence(mockCaseId);
      
      expect(result.graph.keyActors).toEqual([]);
      expect(result.graph.communities).toEqual([]);
      expect(result.risk.factors).toEqual([]);
      expect(result.fraud.patterns).toEqual([]);
      expect(result.reasoning.recommendations).toBeDefined();
    });

    it('should calculate fraud confidence correctly', async () => {
      const result = await intelligenceService.getUnifiedIntelligence(mockCaseId);
      
      expect(result.fraud.confidence).toBeGreaterThanOrEqual(0);
      expect(result.fraud.confidence).toBeLessThanOrEqual(1);
    });

    it('should determine investigation priority based on metrics', async () => {
      const result = await intelligenceService.getUnifiedIntelligence(mockCaseId);
      
      const priorities = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'];
      expect(priorities).toContain(result.metrics.investigationPriority);
    });
  });

  describe('fetchGraphIntelligence', () => {
    it('should fetch graph intelligence correctly', async () => {
      const graphData = await intelligenceService['fetchGraphIntelligence'](mockCaseId);
      
      expect(graphData.keyActors).toBeDefined();
      expect(graphData.communities).toBeDefined();
      expect(graphData.metrics).toBeDefined();
      expect(graphData.collusionRisk).toBeDefined();
    });
  });

  describe('fetchRiskIntelligence', () => {
    it('should fetch risk intelligence correctly', async () => {
      const riskData = await intelligenceService['fetchRiskIntelligence'](mockCaseId);
      
      expect(riskData.score).toBeDefined();
      expect(riskData.level).toBeDefined();
      expect(riskData.factors).toBeDefined();
      expect(riskData.explanations).toBeDefined();
      expect(riskData.trend).toBeDefined();
    });
  });
});