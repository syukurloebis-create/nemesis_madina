// Use relative imports
import { graphApi, riskApi, fraudApi, intelligenceApi } from '../api';

export const intelligenceService = {
  // Get unified intelligence
  getUnifiedIntelligence: async (caseId: string) => {
    const [graph, risk, fraud, intelligence] = await Promise.all([
      graphApi.getKeyActors({ case_id: caseId }).catch(() => ({ data: [] })),
      riskApi.getExplanations(caseId).catch(() => ({})),
      fraudApi.getPatterns(caseId).catch(() => ({ data: [] })),
      intelligenceApi.getGraphRisk(caseId).catch(() => ({})),
    ]);

    return {
      caseId,
      timestamp: new Date(),
      version: '8.0.0',
      graph: { keyActors: graph?.data || [] },
      risk: risk || {},
      fraud: { patterns: fraud?.data || [] },
      intelligence: intelligence || {},
      metrics: {
        overallScore: intelligence?.score || 75,
        confidence: intelligence?.confidence || 0.8,
      },
    };
  },

  // Get reasoning
  getReasoning: async (caseId: string) => {
    const intelligence = await intelligenceService.getUnifiedIntelligence(caseId);
    return intelligence.intelligence?.reasoning || [];
  },

  // Get recommendations
  getRecommendations: async (caseId: string) => {
    const intelligence = await intelligenceService.getUnifiedIntelligence(caseId);
    return intelligence.intelligence?.recommendations || [];
  },
};

export default intelligenceService;
