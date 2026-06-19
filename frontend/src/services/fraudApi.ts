// services/fraudApi.ts - Fraud Pattern Detection API
import api from './api';
import { FraudPattern, FraudPatternSummary, FraudPatternProps } from '../types/fraud';

export const fraudApi = {
  // Get all fraud patterns
  getPatterns: async (): Promise<FraudPattern[]> => {
    const response = await api.get('/api/v1/fraud/patterns');
    return response.data;
  },

  // Get pattern by ID
  getPattern: async (id: string): Promise<FraudPattern> => {
    const response = await api.get(`/api/v1/fraud/patterns/${id}`);
    return response.data;
  },

  // Get pattern summary
  getPatternSummary: async (): Promise<FraudPatternSummary> => {
    const response = await api.get('/api/v1/fraud/patterns/summary');
    return response.data;
  },

  // Get pattern library
  getPatternLibrary: async (): Promise<any[]> => {
    const response = await api.get('/api/v1/fraud/patterns/library');
    return response.data;
  },

  // Update pattern status
  updatePatternStatus: async (id: string, status: string): Promise<FraudPattern> => {
    const response = await api.put(`/api/v1/fraud/patterns/${id}/status`, { status });
    return response.data;
  },

  // Investigate pattern
  investigatePattern: async (id: string): Promise<any> => {
    const response = await api.post(`/api/v1/fraud/patterns/${id}/investigate`);
    return response.data;
  },

  // Get pattern indicators
  getPatternIndicators: async (id: string): Promise<any[]> => {
    const response = await api.get(`/api/v1/fraud/patterns/${id}/indicators`);
    return response.data;
  },

  // Get real-time alerts
  getAlerts: async (): Promise<any[]> => {
    const response = await api.get('/api/v1/fraud/alerts');
    return response.data;
  },

  // Dismiss alert
  dismissAlert: async (id: string): Promise<any> => {
    const response = await api.post(`/api/v1/fraud/alerts/${id}/dismiss`);
    return response.data;
  }
};

export default fraudApi;
