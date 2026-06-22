/**
 * Procurement API Service
 */

import { apiClient } from './index';

export interface ProcurementPackage {
  id: number;
  kode_paket: string;
  kode_rup: string;
  tahun_anggaran: number;
  nama_instansi: string;
  satuan_kerja: string;
  nama_penyedia: string;
  nama_paket: string;
  total_nilai: number;
  nilai_pdn: number;
  metode_pengadaan: string;
  status_paket: string;
}

export interface ProcurementStats {
  total_packages: number;
  total_vendors: number;
  total_value: number;
  average_value: number;
  total_years: number;
  years: number[];
}

export const procurementApi = {
  /**
   * Get procurement packages
   */
  getPackages: async (params?: { 
    tahun?: number; 
    penyedia?: string; 
    instansi?: string;
    limit?: number;
    offset?: number;
  }): Promise<ProcurementPackage[]> => {
    const response = await apiClient.get('/api/v1/procurement/packages', { params });
    return response.data;
  },

  /**
   * Get procurement statistics
   */
  getStats: async (): Promise<ProcurementStats> => {
    const response = await apiClient.get('/api/v1/procurement/stats');
    return response.data;
  },

  /**
   * Get packages by vendor
   */
  getByVendor: async (vendorName: string): Promise<ProcurementPackage[]> => {
    const response = await apiClient.get('/api/v1/procurement/vendor', { 
      params: { name: vendorName } 
    });
    return response.data;
  },
};

export default procurementApi;