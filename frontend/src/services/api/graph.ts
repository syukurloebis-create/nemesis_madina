/**
 * Graph API Service - SIMPLE VERSION
 * No complex type exports to avoid Vite issues
 */

import { apiClient } from './index';

export const graphApi = {
  getEntities: async (params?: { case_id?: string; type?: string }) => {
    try {
      const response = await apiClient.get('/api/v1/graph/entities', { params });
      return response.data || [];
    } catch (error) {
      console.warn('[Graph API] Failed to fetch entities:', error);
      return [];
    }
  },

  getRelationships: async (params?: { case_id?: string; type?: string }) => {
    try {
      const response = await apiClient.get('/api/v1/graph/relationships', { params });
      return response.data || [];
    } catch (error) {
      console.warn('[Graph API] Failed to fetch relationships:', error);
      return [];
    }
  },

  getMetrics: async (caseId?: string) => {
    try {
      const response = await apiClient.get('/api/v1/graph/metrics', { params: { case_id: caseId } });
      return response.data || { entities: 0, relationships: 0, relationship_types: {}, entity_types: {} };
    } catch (error) {
      console.warn('[Graph API] Failed to fetch metrics:', error);
      return { entities: 0, relationships: 0, relationship_types: {}, entity_types: {} };
    }
  },

  getCommunities: async (caseId?: string) => {
    try {
      const response = await apiClient.get('/api/v1/graph/communities', { params: { case_id: caseId } });
      return response.data || [];
    } catch (error) {
      console.warn('[Graph API] Failed to fetch communities:', error);
      return [];
    }
  },

  getKeyActors: async (limit: number = 10) => {
    try {
      const response = await apiClient.get('/api/v1/graph/key-actors', { params: { limit } });
      return response.data || [];
    } catch (error) {
      console.warn('[Graph API] Failed to fetch key actors:', error);
      return [];
    }
  },
};

export default graphApi;