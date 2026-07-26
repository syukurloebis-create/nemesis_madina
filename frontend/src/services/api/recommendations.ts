import { apiClient } from './client';

export const recommendationApi = {
  getSummary: async () => {
    const response = await apiClient.get('/api/v1/recommendations/summary');
    return response;
  },
};

export default recommendationApi;
