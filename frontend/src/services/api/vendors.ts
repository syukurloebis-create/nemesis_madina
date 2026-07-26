import { apiClient } from './client';

export const vendorApi = {
  getSuspicious: async () => {
    const response = await apiClient.get('/api/v1/procurement/vendors');
    return response;
  },
};

export default vendorApi;
