import { apiClient } from './client';

export const procurementApi = {
  getRUPStats: async () => {
    const response = await apiClient.get('/api/v1/procurement/stats');
    return response;
  },
};

export default procurementApi;
