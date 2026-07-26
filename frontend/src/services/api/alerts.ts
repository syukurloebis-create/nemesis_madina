import apiClient from './client';

export const alertsApi = {
  getAlerts: (params?: any) =>
    apiClient.get('/api/v1/alerts', { params }),


  getStats: (caseId?: string) =>
    apiClient.get('/api/v1/alerts/stats', {
      params: caseId
        ? { case_id: caseId }
        : undefined
    }),


  acknowledge: (
    id: string,
    data?: any
  ) =>
    apiClient.post(
      `/api/v1/alerts/${id}/acknowledge`,
      data || {}
    ),


  resolve: (
    id: string,
    data?: any
  ) =>
    apiClient.post(
      `/api/v1/alerts/${id}/resolve`,
      data || {}
    ),


  escalate: (
    id: string,
    level?: any,
    reason?: any
  ) =>
    apiClient.post(
      `/api/v1/alerts/${id}/escalate`,
      {
        level,
        reason
      }
    ),

};


export default alertsApi;