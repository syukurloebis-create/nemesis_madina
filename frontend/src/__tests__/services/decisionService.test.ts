// frontend/src/__tests__/services/decisionService.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { decisionService } from '@/services/decisionService';
import { api } from '@/services/api';

vi.mock('@/services/api', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

describe('DecisionService', () => {
  const mockCaseId = 'test-case-123';
  const mockUserId = 'user-456';
  const mockDecision = {
    id: 'dec-1',
    case_id: mockCaseId,
    title: 'Investigate Irregular Transactions',
    description: 'Suspicious transactions detected in procurement',
    impact: 'HIGH',
    confidence: 85,
    status: 'PENDING',
    created_at: '2026-06-22T10:00:00Z',
    evidence: [
      {
        id: 'ev-1',
        type: 'TRANSACTION',
        title: 'Unusual Payment',
        description: 'Payment above threshold',
        confidence: 0.9,
        source: 'SYSTEM',
      },
    ],
    votes: [],
    comments: [],
    tags: ['FRAUD', 'PROCUREMENT'],
  };

  beforeEach(() => {
    vi.clearAllMocks();
    
    (api.get as any).mockImplementation((url: string) => {
      if (url.includes('/recommendations')) {
        return Promise.resolve({ data: [mockDecision] });
      }
      return Promise.resolve({ data: {} });
    });

    (api.post as any).mockResolvedValue({ data: { success: true } });
  });

  describe('getDecisions', () => {
    it('should fetch decisions for a case', async () => {
      const decisions = await decisionService.getDecisions(mockCaseId);
      
      expect(decisions).toHaveLength(1);
      expect(decisions[0].id).toBe('dec-1');
      expect(decisions[0].title).toBe('Investigate Irregular Transactions');
      expect(api.get).toHaveBeenCalledWith('/api/v1/recommendations', {
        params: { case_id: mockCaseId },
      });
    });

    it('should transform decisions correctly', async () => {
      const decisions = await decisionService.getDecisions(mockCaseId);
      const decision = decisions[0];
      
      expect(decision).toHaveProperty('id');
      expect(decision).toHaveProperty('caseId');
      expect(decision).toHaveProperty('type');
      expect(decision).toHaveProperty('title');
      expect(decision).toHaveProperty('description');
      expect(decision).toHaveProperty('impact');
      expect(decision).toHaveProperty('confidence');
      expect(decision).toHaveProperty('status');
      expect(decision).toHaveProperty('createdAt');
      expect(decision).toHaveProperty('updatedAt');
      expect(decision).toHaveProperty('evidence');
      expect(decision).toHaveProperty('votes');
      expect(decision).toHaveProperty('comments');
      expect(decision).toHaveProperty('tags');
    });

    it('should handle empty responses', async () => {
      (api.get as any).mockResolvedValueOnce({ data: [] });
      
      const decisions = await decisionService.getDecisions(mockCaseId);
      expect(decisions).toEqual([]);
    });
  });

  describe('createDecision', () => {
    it('should create a new decision', async () => {
      const mockEvidence = [
        {
          id: 'ev-1',
          type: 'DOCUMENT',
          title: 'Procurement Document',
          description: 'Suspicious contract',
          confidence: 0.85,
          source: 'USER',
        },
      ];
      
      const decision = await decisionService.createDecision(
        mockCaseId,
        'Review Procurement Process',
        'Irregularities found in procurement process',
        'HIGH',
        80,
        mockEvidence,
        'AI analysis detected anomalies'
      );
      
      expect(decision).toBeDefined();
      expect(api.post).toHaveBeenCalledWith('/api/v1/recommendations', {
        case_id: mockCaseId,
        title: 'Review Procurement Process',
        description: 'Irregularities found in procurement process',
        impact: 'HIGH',
        confidence: 80,
        evidence: mockEvidence,
        explanation: 'AI analysis detected anomalies',
        type: 'RECOMMENDATION',
      });
    });

    it('should auto-approve decisions with high confidence', async () => {
      const mockEvidence = [
        {
          id: 'ev-1',
          type: 'AI_ANALYSIS',
          title: 'High Confidence Detection',
          description: 'Pattern matched with 95% confidence',
          confidence: 0.95,
          source: 'AI',
        },
      ];
      
      await decisionService.createDecision(
        mockCaseId,
        'Auto-approve Test',
        'High confidence decision',
        'HIGH',
        95,
        mockEvidence,
        'Auto-approved due to high confidence'
      );
      
      // Should call approve endpoint after creation
      expect(api.post).toHaveBeenCalledWith(
        '/api/v1/recommendations/dec-1/approve',
        expect.any(Object)
      );
    });
  });

  describe('approveDecision', () => {
    it('should approve a decision', async () => {
      await decisionService.approveDecision('dec-1', 'Approved by team', mockUserId);
      
      expect(api.post).toHaveBeenCalledWith('/api/v1/recommendations/dec-1/approve', {
        comment: 'Approved by team',
        user_id: mockUserId,
      });
    });
  });

  describe('rejectDecision', () => {
    it('should reject a decision', async () => {
      await decisionService.rejectDecision('dec-1', 'Not enough evidence', mockUserId);
      
      expect(api.post).toHaveBeenCalledWith('/api/v1/recommendations/dec-1/reject', {
        reason: 'Not enough evidence',
        user_id: mockUserId,
      });
    });
  });

  describe('voteDecision', () => {
    it('should vote on a decision', async () => {
      const vote = {
        userId: mockUserId,
        userName: 'John Doe',
        vote: 'APPROVE' as const,
        comment: 'Looks good to me',
        timestamp: new Date(),
      };
      
      await decisionService.voteDecision('dec-1', vote);
      
      expect(api.post).toHaveBeenCalledWith('/api/v1/recommendations/dec-1/vote', vote);
    });
  });

  describe('escalateDecision', () => {
    it('should escalate a decision', async () => {
      await decisionService.escalateDecision('dec-1', 'Needs senior review');
      
      expect(api.post).toHaveBeenCalledWith('/api/v1/recommendations/dec-1/escalate', {
        reason: 'Needs senior review',
      });
    });
  });

  describe('shouldAutoImplement', () => {
    it('should auto-implement decisions with high confidence and approvals', () => {
      const decision = {
        ...mockDecision,
        confidence: 95,
        status: 'APPROVED' as const,
        votes: [
          { userId: 'user-1', userName: 'User 1', vote: 'APPROVE' as const, timestamp: new Date() },
          { userId: 'user-2', userName: 'User 2', vote: 'APPROVE' as const, timestamp: new Date() },
        ],
      };
      
      const shouldImplement = decisionService['shouldAutoImplement'](decision);
      expect(shouldImplement).toBe(true);
    });

    it('should not auto-implement if confidence is low', () => {
      const decision = {
        ...mockDecision,
        confidence: 60,
        status: 'APPROVED' as const,
        votes: [],
      };
      
      const shouldImplement = decisionService['shouldAutoImplement'](decision);
      expect(shouldImplement).toBe(false);
    });

    it('should not auto-implement if not approved', () => {
      const decision = {
        ...mockDecision,
        confidence: 95,
        status: 'PENDING' as const,
        votes: [],
      };
      
      const shouldImplement = decisionService['shouldAutoImplement'](decision);
      expect(shouldImplement).toBe(false);
    });

    it('should not auto-implement if there are rejections', () => {
      const decision = {
        ...mockDecision,
        confidence: 95,
        status: 'APPROVED' as const,
        votes: [
          { userId: 'user-1', userName: 'User 1', vote: 'REJECT' as const, timestamp: new Date() },
        ],
      };
      
      const shouldImplement = decisionService['shouldAutoImplement'](decision);
      expect(shouldImplement).toBe(false);
    });
  });
});