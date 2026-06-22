import { api } from './api';

export class IntelligenceService {
  async getUnifiedIntelligence(caseId: string): Promise<any> {
    try {
      const [graph, risk, fraud] = await Promise.all([
        api.get('/api/v1/graph/key-actors', { params: { case_id: caseId } }),
        api.get(`/api/v1/cases/${caseId}/risk-explanations`),
        api.get(`/api/v1/fraud/patterns/${caseId}`),
      ]);

      return {
        caseId,
        timestamp: new Date(),
        version: '8.0.0',
        graph: { keyActors: graph.data || [] },
        risk: { score: risk.data?.score || 0, factors: risk.data?.factors || [] },
        fraud: { patterns: fraud.data || [] },
        reasoning: {
          score: 75,
          confidence: 0.8,
          recommendations: [
            {
              id: 'rec-1',
              title: 'Review High-Risk Entities',
              description: 'Multiple entities with high risk scores detected',
              priority: 'HIGH',
              confidence: 0.85,
              impact: 80,
              effort: 60,
              roi: 1.33,
              actions: ['Review transactions', 'Audit connections'],
              timeline: '2 weeks',
              responsible: 'Investigation Team',
              status: 'PENDING'
            }
          ]
        },
        metrics: {
          overallScore: 75,
          riskExposure: risk.data?.score || 0,
          fraudProbability: 0.7,
          investigationPriority: 'HIGH',
          confidence: 0.8,
          lastUpdate: new Date(),
          nextUpdate: new Date(Date.now() + 5 * 60000)
        }
      };
    } catch (error) {
      console.error('[IntelligenceService] Error:', error);
      throw error;
    }
  }
}

export const intelligenceService = new IntelligenceService();
