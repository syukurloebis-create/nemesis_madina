import { apiClient } from './client';

export const procurementApi = {
  // Get RUP packages
  getRUPPackages: (params?: any) => 
    apiClient.get('/api/v1/procurement/rup', { params }),
  
  // Get RUP stats
  getRUPStats: () => 
    apiClient.get('/api/v1/procurement/stats'),
  
  // Get vendors
  getVendors: () => 
    apiClient.get('/api/v1/procurement/vendors'),
  
  // Get vendor details
  getVendor: (vendorId: string) => 
    apiClient.get(`/api/v1/procurement/vendors/${vendorId}`),
};

export default procurementApi;
