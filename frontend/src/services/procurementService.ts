import { api } from './api';
import type { ProcurementPackage, ProcurementStats } from '../types/procurement';

// Mock data dengan vendor yang lebih lengkap
const MOCK_PACKAGES: ProcurementPackage[] = [
  {
    id: '1',
    package_name: 'Pengadaan Perangkat Keras Server',
    budget: 2500000000,
    budget_year: 2026,
    procurement_method: 'Tender',
    status: 'tendering',
    vendor_name: 'PT. Maju Jaya',
    vendor_id: '1',
    risk_score: 75,
    risk_level: 'high',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  },
  {
    id: '2',
    package_name: 'Pengembangan Aplikasi Intelligence',
    budget: 1800000000,
    budget_year: 2026,
    procurement_method: 'Pengadaan Langsung',
    status: 'planning',
    vendor_name: 'CV. Karya Mandiri',
    vendor_id: '2',
    risk_score: 45,
    risk_level: 'medium',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  },
  {
    id: '3',
    package_name: 'Jasa Konsultan Keamanan Siber',
    budget: 750000000,
    budget_year: 2026,
    procurement_method: 'Seleksi',
    status: 'tendering',
    vendor_name: 'PT. Bangun Nusantara',
    vendor_id: '3',
    risk_score: 85,
    risk_level: 'critical',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  },
  {
    id: '4',
    package_name: 'Sistem Pengelolaan Database',
    budget: 520000000,
    budget_year: 2025,
    procurement_method: 'Tender',
    status: 'contract',
    vendor_name: 'PT. Maju Jaya',
    vendor_id: '1',
    contract_value: 510000000,
    risk_score: 68,
    risk_level: 'medium',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  },
  {
    id: '5',
    package_name: 'Pelatihan Analis Data',
    budget: 350000000,
    budget_year: 2026,
    procurement_method: 'Pengadaan Langsung',
    status: 'planning',
    vendor_name: 'CV. Karya Mandiri',
    vendor_id: '2',
    risk_score: 30,
    risk_level: 'low',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  },
  {
    id: '6',
    package_name: 'Pengadaan Lisensi Software',
    budget: 900000000,
    budget_year: 2026,
    procurement_method: 'Tender',
    status: 'tendering',
    vendor_name: null,
    risk_score: 55,
    risk_level: 'medium',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  },
  {
    id: '7',
    package_name: 'Pengadaan Jaringan Data Center',
    budget: 1200000000,
    budget_year: 2026,
    procurement_method: 'Tender',
    status: 'planning',
    vendor_name: 'PT. Bangun Nusantara',
    vendor_id: '3',
    risk_score: 72,
    risk_level: 'high',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  },
];

class ProcurementService {
  async getPackages(params?: { status?: string; year?: number }): Promise<ProcurementPackage[]> {
    try {
      const response = await api.get('/procurement/packages');
      return response.data || response || [];
    } catch (error) {
      console.log('Using mock procurement data');
      let packages = [...MOCK_PACKAGES];
      if (params?.status && params.status !== 'all') {
        packages = packages.filter(p => p.status === params.status);
      }
      if (params?.year) {
        packages = packages.filter(p => p.budget_year === params.year);
      }
      return packages;
    }
  }

  async getStats(): Promise<ProcurementStats> {
    try {
      const response = await api.get('/procurement/stats');
      return response.data || response;
    } catch (error) {
      const packages = MOCK_PACKAGES;
      const by_status: Record<string, number> = {};
      const by_method: Record<string, number> = {};
      
      packages.forEach(p => {
        by_status[p.status] = (by_status[p.status] || 0) + 1;
        by_method[p.procurement_method] = (by_method[p.procurement_method] || 0) + 1;
      });
      
      return {
        total_packages: packages.length,
        total_budget: packages.reduce((sum, p) => sum + p.budget, 0),
        total_contract_value: packages.reduce((sum, p) => sum + (p.contract_value || 0), 0),
        avg_risk_score: Math.round(packages.reduce((sum, p) => sum + (p.risk_score || 0), 0) / packages.length),
        by_status,
        by_method
      };
    }
  }
}

export const procurementService = new ProcurementService();
