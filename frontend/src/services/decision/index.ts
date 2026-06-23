import { apiClient } from '../api/client';
import type { Decision, DecisionFilter, DecisionStats, DecisionAction } from '@/types/decision';

export class DecisionService {
  private static instance: DecisionService;
  private cache: Map<string, { data: Decision[]; timestamp: number }> = new Map();
  private CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

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
      const response = await apiClient.post('/api/v1/recommendations', {
        case_id: data.caseId,
        title: data.title,
        description: data.description,
        priority: data.priority,
        confidence: data.confidence,
        evidence: data.evidence,
        type: data.type || 'RECOMMENDATION',
      });
      
      const decision = this.transformDecision(response.data);
      this.invalidateCache(data.caseId!);
      return decision;
    } catch (error) {
      console.error('[DecisionService] Failed to create decision:', error);
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
      
      const decision = this.transformDecision(response.data);
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
      
      const decision = this.transformDecision(response.data);
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
      
      const decision = this.transformDecision(response.data);
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
      
      const decision = this.transformDecision(response.data);
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
      const decision = this.transformDecision(response.data);
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
      
      const decision = this.transformDecision(response.data);
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
   * Get available actions for a decision
   */
  getActionsForDecision(decision: Decision, userId: string): DecisionAction[] {
    const actions: DecisionAction[] = [];

    // Check if user is the creator or assigned
    const isCreator = decision.createdBy === userId;
    const isAssigned = decision.assignedTo === userId;

    // PENDING decisions
    if (decision.status === 'PENDING') {
      // Creator can edit or cancel
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

      // Assigned user can review
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

      // Any user can vote
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

    // HIGH priority decisions - can escalate
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

  // Private helper methods
  private transformDecisions(data: any[]): Decision[] {
    return data.map(item => this.transformDecision(item));
  }

  private transformDecision(data: any): Decision {
    return {
      id: data.id || data.recommendation_id,
      caseId: data.case_id || data.caseId,
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
        totalApprovalTime += timeDiff / (1000 * 60 * 60); // hours
      }
    });

    // Calculate averages
    stats.averageApprovalTime = approvedCount > 0 ? totalApprovalTime / approvedCount : 0;
    stats.approvalRate = decisions.length > 0 ? (approvedCount / decisions.length) * 100 : 0;

    return stats;
  }

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

  private invalidateCache(caseId: string): void {
    const keys = Array.from(this.cache.keys());
    keys.forEach(key => {
      if (key.startsWith(caseId)) {
        this.cache.delete(key);
      }
    });
  }
}

export const decisionService = DecisionService.getInstance();
export default decisionService;
