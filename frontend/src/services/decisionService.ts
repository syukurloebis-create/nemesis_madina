import { api } from './api';

export class DecisionService {
  async getDecisions(caseId: string): Promise<any[]> {
    try {
      const response = await api.get('/api/v1/recommendations', {
        params: { case_id: caseId },
      });
      return response.data || [];
    } catch (error) {
      console.error('[DecisionService] Error:', error);
      return [];
    }
  }

  async getDecision(id: string): Promise<any> {
    const response = await api.get(`/api/v1/recommendations/${id}`);
    return response.data;
  }

  async createDecision(data: any): Promise<any> {
    const response = await api.post('/api/v1/recommendations', data);
    return response.data;
  }

  async approveDecision(id: string, comment: string, userId: string): Promise<void> {
    await api.post(`/api/v1/recommendations/${id}/approve`, { comment, user_id: userId });
  }

  async rejectDecision(id: string, reason: string, userId: string): Promise<void> {
    await api.post(`/api/v1/recommendations/${id}/reject`, { reason, user_id: userId });
  }

  async implementDecision(id: string): Promise<void> {
    await api.post(`/api/v1/recommendations/${id}/implement`);
  }

  async escalateDecision(id: string, reason: string): Promise<void> {
    await api.post(`/api/v1/recommendations/${id}/escalate`, { reason });
  }

  async voteDecision(id: string, vote: any): Promise<void> {
    await api.post(`/api/v1/recommendations/${id}/vote`, vote);
  }
}

export const decisionService = new DecisionService();
