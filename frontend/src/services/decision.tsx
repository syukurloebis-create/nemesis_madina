/**
 * NEMESIS V8+ - Decision Service
 * Unified service for decision management
 */

import { apiClient } from './api/client';

export interface Decision {
  id: string;
  caseId: string;
  title: string;
  description: string;
  type: 'RECOMMENDATION' | 'ACTION' | 'APPROVAL' | 'ESCALATION';
  status: 'PENDING' | 'APPROVED' | 'REJECTED' | 'IMPLEMENTED' | 'ESCALATED' | 'IN_REVIEW';
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  confidence: number;
  createdAt: Date;
  updatedAt: Date;
  createdBy: string;
  createdByName: string;
  assignedTo?: string;
  assignedToName?: string;
  dueDate?: Date;
  approvedAt?: Date;
  approvedBy?: string;
  approvedByName?: string;
  rejectionReason?: string;
  implementationNotes?: string;
  evidence: DecisionEvidence[];
  votes: DecisionVote[];
  comments: DecisionComment[];
  tags: string[];
  actions: DecisionAction[];
}

export interface DecisionEvidence {
  id: string;
  type: 'DOCUMENT' | 'TRANSACTION' | 'RELATIONSHIP' | 'PATTERN' | 'STATEMENT';
  title: string;
  description: string;
  confidence: number;
  source: string;
  url?: string;
  referenceId?: string;
}

export interface DecisionVote {
  userId: string;
  userName: string;
  vote: 'APPROVE' | 'REJECT' | 'ABSTAIN' | 'ESCALATE';
  comment?: string;
  timestamp: Date;
}

export interface DecisionComment {
  id: string;
  userId: string;
  userName: string;
  content: string;
  timestamp: Date;
  parentId?: string;
}

export interface DecisionAction {
  id: string;
  type: 'INVESTIGATE' | 'REVIEW' | 'ESCALATE' | 'IMPLEMENT' | 'REJECT' | 'APPROVE';
  label: string;
  description: string;
  priority: number;
  handler: (decision: Decision) => Promise<void>;
  isEnabled: boolean;
  isVisible: boolean;
}

export interface DecisionFilter {
  status?: Decision['status'][];
  priority?: Decision['priority'][];
  type?: Decision['type'][];
  search?: string;
  assignedTo?: string;
  fromDate?: Date;
  toDate?: Date;
}

export interface DecisionStats {
  total: number;
  pending: number;
  approved: number;
  rejected: number;
  implemented: number;
  escalated: number;
  byPriority: {
    LOW: number;
    MEDIUM: number;
    HIGH: number;
    CRITICAL: number;
  };
  byType: {
    RECOMMENDATION: number;
    ACTION: number;
    APPROVAL: number;
    ESCALATION: number;
  };
  averageApprovalTime: number;
  approvalRate: number;
}

class DecisionService {
  private static instance: DecisionService;
  private cache: Map<string, { data: Decision[]; timestamp: number }> = new Map();
  private CACHE_DURATION = 5 * 60 * 1000;

  private constructor() {}

  public static getInstance(): DecisionService {
    if (!DecisionService.instance) {
      DecisionService.instance = new DecisionService();
    }
    return DecisionService.instance;
  }

  /**
   * Get all decisions for a case
   */
  async getDecisions(caseId: string, filter?: DecisionFilter): Promise<Decision[]> {
    const cacheKey = `${caseId}-${JSON.stringify(filter)}`;
    const cached = this.cache.get(cacheKey);
    
    if (cached && (Date.now() - cached.timestamp) < this.CACHE_DURATION) {
      return cached.data;
    }

    try {
      const response = await apiClient.get('/api/v1/recommendations', {
        params: { case_id: caseId, ...filter },
      });
      
      const decisions = this.transformDecisions(response.data || []);
      this.cache.set(cacheKey, { data: decisions, timestamp: Date.now() });
      return decisions;
    } catch (error) {
      console.error('[DecisionService] Failed to fetch decisions:', error);
      return [];
    }
  }

  /**
   * Get a single decision by ID
   */
  async getDecision(id: string): Promise<Decision | null> {
    try {
      const response = await apiClient.get(`/api/v1/recommendations/${id}`);
      return this.transformDecision(response.data);
    } catch (error) {
      console.error('[DecisionService] Failed to fetch decision:', error);
      return null;
    }
  }

  /**
   * Create a new decision
   */
  async createDecision(data: Partial<Decision>): Promise<Decision> {
    try {
      const payload = {
        case_id: data.caseId,
        title: data.title,
        description: data.description,
        priority: data.priority || 'MEDIUM',
        confidence: data.confidence || 50,
        evidence: data.evidence || [],
        type: data.type || 'RECOMMENDATION',
        assigned_to: data.assignedTo,
        due_date: data.dueDate,
        tags: data.tags || [],
      };

      const response = await apiClient.post('/api/v1/recommendations', payload);
      const decision = this.transformDecision(response.data || {});
      this.invalidateCache(decision.caseId);
      return decision;
    } catch (error) {
      console.error('[DecisionService] Failed to create decision:', error);
      throw error;
    }
  }

  /**
   * Update a decision
   */
  async updateDecision(id: string, data: Partial<Decision>): Promise<Decision> {
    try {
      const response = await apiClient.put(`/api/v1/recommendations/${id}`, data);
      const decision = this.transformDecision(response.data || {});
      this.invalidateCache(decision.caseId);
      return decision;
    } catch (error) {
      console.error('[DecisionService] Failed to update decision:', error);
      throw error;
    }
  }

  /**
   * Approve a decision
   */
  async approveDecision(id: string, comment: string, userId: string): Promise<Decision> {
    try {
      const response = await apiClient.post(`/api/v1/recommendations/${id}/approve`, {
        comment,
        user_id: userId,
      });
      
      const decision = this.transformDecision(response.data || {});
      this.invalidateCache(decision.caseId);
      return decision;
    } catch (error) {
      console.error('[DecisionService] Failed to approve decision:', error);
      throw error;
    }
  }

  /**
   * Reject a decision
   */
  async rejectDecision(id: string, reason: string, userId: string): Promise<Decision> {
    try {
      const response = await apiClient.post(`/api/v1/recommendations/${id}/reject`, {
        reason,
        user_id: userId,
      });
      
      const decision = this.transformDecision(response.data || {});
      this.invalidateCache(decision.caseId);
      return decision;
    } catch (error) {
      console.error('[DecisionService] Failed to reject decision:', error);
      throw error;
    }
  }

  /**
   * Implement a decision
   */
  async implementDecision(id: string, notes: string): Promise<Decision> {
    try {
      const response = await apiClient.post(`/api/v1/recommendations/${id}/implement`, {
        notes,
      });
      
      const decision = this.transformDecision(response.data || {});
      this.invalidateCache(decision.caseId);
      return decision;
    } catch (error) {
      console.error('[DecisionService] Failed to implement decision:', error);
      throw error;
    }
  }

  /**
   * Escalate a decision
   */
  async escalateDecision(id: string, reason: string): Promise<Decision> {
    try {
      const response = await apiClient.post(`/api/v1/recommendations/${id}/escalate`, {
        reason,
      });
      
      const decision = this.transformDecision(response.data || {});
      this.invalidateCache(decision.caseId);
      return decision;
    } catch (error) {
      console.error('[DecisionService] Failed to escalate decision:', error);
      throw error;
    }
  }

  /**
   * Vote on a decision
   */
  async voteDecision(id: string, vote: Omit<DecisionVote, 'timestamp'>): Promise<Decision> {
    try {
      const response = await apiClient.post(`/api/v1/recommendations/${id}/vote`, vote);
      const decision = this.transformDecision(response.data || {});
      this.invalidateCache(decision.caseId);
      return decision;
    } catch (error) {
      console.error('[DecisionService] Failed to vote on decision:', error);
      throw error;
    }
  }

  /**
   * Add a comment to a decision
   */
  async addComment(id: string, content: string, userId: string): Promise<Decision> {
    try {
      const response = await apiClient.post(`/api/v1/recommendations/${id}/comments`, {
        content,
        user_id: userId,
      });
      
      const decision = this.transformDecision(response.data || {});
      this.invalidateCache(decision.caseId);
      return decision;
    } catch (error) {
      console.error('[DecisionService] Failed to add comment:', error);
      throw error;
    }
  }

  /**
   * Get decision statistics
   */
  async getStats(caseId: string): Promise<DecisionStats> {
    try {
      const decisions = await this.getDecisions(caseId);
      return this.calculateStats(decisions);
    } catch (error) {
      console.error('[DecisionService] Failed to get stats:', error);
      return this.getEmptyStats();
    }
  }

  /**
   * Invalidate cache for a case
   */
  private invalidateCache(caseId: string): void {
    const keys = Array.from(this.cache.keys());
    keys.forEach(key => {
      if (key.startsWith(caseId)) {
        this.cache.delete(key);
      }
    });
  }

  /**
   * Transform decisions from API response
   */
  private transformDecisions(data: any[]): Decision[] {
    if (!data || !Array.isArray(data)) return [];
    return data.map(item => this.transformDecision(item));
  }

  /**
   * Transform a single decision from API response
   */
  private transformDecision(data: any): Decision {
    if (!data || typeof data !== 'object') {
      return this.getDefaultDecision();
    }

    return {
      id: data.id || data.recommendation_id || 'unknown',
      caseId: data.case_id || data.caseId || '',
      title: data.title || 'Untitled Decision',
      description: data.description || '',
      type: data.type || data.recommendation_type || 'RECOMMENDATION',
      status: data.status || 'PENDING',
      priority: data.priority || 'MEDIUM',
      confidence: data.confidence || data.confidence_score || 0,
      createdAt: new Date(data.created_at || data.timestamp || Date.now()),
      updatedAt: new Date(data.updated_at || Date.now()),
      createdBy: data.created_by || data.creator || 'system',
      createdByName: data.created_by_name || 'System',
      assignedTo: data.assigned_to,
      assignedToName: data.assigned_to_name,
      dueDate: data.due_date ? new Date(data.due_date) : undefined,
      approvedAt: data.approved_at ? new Date(data.approved_at) : undefined,
      approvedBy: data.approved_by,
      approvedByName: data.approved_by_name,
      rejectionReason: data.rejection_reason,
      implementationNotes: data.implementation_notes,
      evidence: data.evidence || [],
      votes: data.votes || [],
      comments: data.comments || [],
      tags: data.tags || [],
      actions: [],
    };
  }

  /**
   * Get default/empty decision
   */
  private getDefaultDecision(): Decision {
    return {
      id: 'unknown',
      caseId: '',
      title: 'Unknown Decision',
      description: '',
      type: 'RECOMMENDATION',
      status: 'PENDING',
      priority: 'MEDIUM',
      confidence: 0,
      createdAt: new Date(),
      updatedAt: new Date(),
      createdBy: 'system',
      createdByName: 'System',
      evidence: [],
      votes: [],
      comments: [],
      tags: [],
      actions: [],
    };
  }

  /**
   * Calculate decision statistics
   */
  private calculateStats(decisions: Decision[]): DecisionStats {
    const stats: DecisionStats = {
      total: decisions.length,
      pending: 0,
      approved: 0,
      rejected: 0,
      implemented: 0,
      escalated: 0,
      byPriority: { LOW: 0, MEDIUM: 0, HIGH: 0, CRITICAL: 0 },
      byType: { RECOMMENDATION: 0, ACTION: 0, APPROVAL: 0, ESCALATION: 0 },
      averageApprovalTime: 0,
      approvalRate: 0,
    };

    let totalApprovalTime = 0;
    let approvedCount = 0;

    decisions.forEach(d => {
      // Count status
      switch (d.status) {
        case 'PENDING': stats.pending++; break;
        case 'APPROVED': stats.approved++; approvedCount++; break;
        case 'REJECTED': stats.rejected++; break;
        case 'IMPLEMENTED': stats.implemented++; break;
        case 'ESCALATED': stats.escalated++; break;
      }

      // Count priority
      stats.byPriority[d.priority]++;

      // Count type
      stats.byType[d.type]++;

      // Calculate approval time
      if (d.approvedAt && d.createdAt) {
        const timeDiff = d.approvedAt.getTime() - d.createdAt.getTime();
        totalApprovalTime += timeDiff / (1000 * 60 * 60);
      }
    });

    stats.averageApprovalTime = approvedCount > 0 ? totalApprovalTime / approvedCount : 0;
    stats.approvalRate = decisions.length > 0 ? (approvedCount / decisions.length) * 100 : 0;

    return stats;
  }

  /**
   * Get empty statistics
   */
  private getEmptyStats(): DecisionStats {
    return {
      total: 0,
      pending: 0,
      approved: 0,
      rejected: 0,
      implemented: 0,
      escalated: 0,
      byPriority: { LOW: 0, MEDIUM: 0, HIGH: 0, CRITICAL: 0 },
      byType: { RECOMMENDATION: 0, ACTION: 0, APPROVAL: 0, ESCALATION: 0 },
      averageApprovalTime: 0,
      approvalRate: 0,
    };
  }

  /**
   * Get available actions for a decision based on user role
   */
  getActionsForDecision(decision: Decision, userId: string): DecisionAction[] {
    const actions: DecisionAction[] = [];

    const isCreator = decision.createdBy === userId;
    const isAssigned = decision.assignedTo === userId;

    // PENDING decisions
    if (decision.status === 'PENDING') {
      if (isCreator) {
        actions.push({
          id: `edit-${decision.id}`,
          type: 'REVIEW',
          label: 'Edit Decision',
          description: 'Modify decision details',
          priority: 1,
          handler: async () => {},
          isEnabled: true,
          isVisible: true,
        });
      }

      if (isAssigned || isCreator) {
        actions.push({
          id: `review-${decision.id}`,
          type: 'REVIEW',
          label: 'Review Decision',
          description: 'Review decision details',
          priority: 2,
          handler: async () => {},
          isEnabled: true,
          isVisible: true,
        });
      }

      actions.push({
        id: `vote-${decision.id}`,
        type: 'APPROVE',
        label: 'Vote',
        description: 'Approve or reject this decision',
        priority: 3,
        handler: async () => {},
        isEnabled: true,
        isVisible: true,
      });
    }

    // APPROVED decisions - can implement
    if (decision.status === 'APPROVED') {
      actions.push({
        id: `implement-${decision.id}`,
        type: 'IMPLEMENT',
        label: 'Implement Decision',
        description: 'Execute this decision',
        priority: 1,
        handler: async () => {},
        isEnabled: true,
        isVisible: true,
      });
    }

    // HIGH/CRITICAL priority - can escalate
    if (decision.priority === 'HIGH' || decision.priority === 'CRITICAL') {
      actions.push({
        id: `escalate-${decision.id}`,
        type: 'ESCALATE',
        label: 'Escalate',
        description: 'Escalate to higher authority',
        priority: 4,
        handler: async () => {},
        isEnabled: true,
        isVisible: true,
      });
    }

    return actions.sort((a, b) => a.priority - b.priority);
  }
}

// Export singleton instance
export const decisionService = DecisionService.getInstance();
export default decisionService;
