import { api } from './api';
import type { Vendor, VendorContract, VendorCollusion, VendorRiskFactor } from '../types/vendor';

class VendorService {
  // Get all vendors
  async getVendors(params?: { search?: string; risk_level?: string; status?: string }): Promise<Vendor[]> {
    try {
      const queryParams = new URLSearchParams(params as any).toString();
      const response = await api.get(`/vendors${queryParams ? `?${queryParams}` : ''}`);
      return response.data || response || [];
    } catch (error) {
      console.error('Failed to fetch vendors:', error);
      // Return mock data for demo
      return this.getMockVendors();
    }
  }

  // Get vendor by ID
  async getVendor(id: string): Promise<Vendor | null> {
    try {
      const response = await api.get(`/vendors/${id}`);
      return response.data || response;
    } catch (error) {
      console.error('Failed to fetch vendor:', error);
      const mockVendors = this.getMockVendors();
      return mockVendors.find(v => v.id === id) || null;
    }
  }

  // Get vendor contracts
  async getVendorContracts(vendorId: string): Promise<VendorContract[]> {
    try {
      const response = await api.get(`/vendors/${vendorId}/contracts`);
      return response.data || response || [];
    } catch (error) {
      console.error('Failed to fetch vendor contracts:', error);
      return [];
    }
  }

  // Get vendor collusions
  async getVendorCollusions(vendorId?: string): Promise<VendorCollusion[]> {
    try {
      const url = vendorId ? `/collusions?vendor_id=${vendorId}` : '/collusions';
      const response = await api.get(url);
      return response.data || response || [];
    } catch (error) {
      console.error('Failed to fetch collusions:', error);
      return this.getMockCollusions();
    }
  }

  // Get vendor risk factors
  async getVendorRiskFactors(vendorId: string): Promise<VendorRiskFactor[]> {
    try {
      const response = await api.get(`/vendors/${vendorId}/risk-factors`);
      return response.data || response || [];
    } catch (error) {
      console.error('Failed to fetch risk factors:', error);
      return [];
    }
  }

  // Create vendor
  async createVendor(data: Partial<Vendor>): Promise<Vendor | null> {
    try {
      const response = await api.post('/vendors', data);
      return response.data || response;
    } catch (error) {
      console.error('Failed to create vendor:', error);
      return null;
    }
  }

  // Update vendor
  async updateVendor(id: string, data: Partial<Vendor>): Promise<Vendor | null> {
    try {
      const response = await api.put(`/vendors/${id}`, data);
      return response.data || response;
    } catch (error) {
      console.error('Failed to update vendor:', error);
      return null;
    }
  }

  // Link vendor to case
  async linkVendorToCase(vendorId: string, caseId: string): Promise<boolean> {
    try {
      await api.post(`/vendors/${vendorId}/cases/${caseId}`);
      return true;
    } catch (error) {
      console.error('Failed to link vendor to case:', error);
      return false;
    }
  }

  // Mock data for demo
  private getMockVendors(): Vendor[] {
    return [
      {
        id: '1',
        name: 'PT. Maju Jaya',
        registration_number: '1234567890',
        tax_id: '01.234.567.8-901.000',
        address: 'Jl. Sudirman No. 123',
        city: 'Jakarta Selatan',
        province: 'DKI Jakarta',
        postal_code: '12190',
        phone: '021-1234567',
        email: 'info@majujaya.co.id',
        website: 'www.majujaya.co.id',
        established_year: 2010,
        business_type: 'Kontraktor',
        classification: 'large',
        risk_score: 92,
        risk_level: 'critical',
        status: 'active',
        related_cases: 5,
        total_contracts: 12,
        total_value: 450,
        last_audit: '2026-05-15',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        metadata: {}
      },
      {
        id: '2',
        name: 'CV. Karya Mandiri',
        registration_number: '9876543210',
        tax_id: '02.345.678.9-012.000',
        address: 'Jl. Gatot Subroto No. 45',
        city: 'Jakarta Pusat',
        province: 'DKI Jakarta',
        postal_code: '10270',
        phone: '021-7654321',
        email: 'cs@karyamandiri.com',
        website: 'www.karyamandiri.com',
        established_year: 2015,
        business_type: 'Penyedia Jasa',
        classification: 'medium',
        risk_score: 88,
        risk_level: 'high',
        status: 'active',
        related_cases: 3,
        total_contracts: 8,
        total_value: 280,
        last_audit: '2026-04-20',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        metadata: {}
      },
      {
        id: '3',
        name: 'PT. Bangun Nusantara',
        registration_number: '5555555555',
        tax_id: '03.456.789.0-123.000',
        address: 'Jl. Thamrin No. 78',
        city: 'Jakarta Pusat',
        province: 'DKI Jakarta',
        postal_code: '10350',
        phone: '021-5551234',
        email: 'info@bangunnusantara.com',
        website: 'www.bangunnusantara.com',
        established_year: 2008,
        business_type: 'Konstruksi',
        classification: 'large',
        risk_score: 78,
        risk_level: 'medium',
        status: 'active',
        related_cases: 2,
        total_contracts: 15,
        total_value: 620,
        last_audit: '2026-03-10',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        metadata: {}
      },
    ];
  }

  private getMockCollusions(): VendorCollusion[] {
    return [
      {
        id: '1',
        vendor_ids: ['1', '2'],
        pattern_type: 'address',
        confidence: 92,
        severity: 'high',
        description: 'Multiple vendors sharing same registered address pattern',
        detected_at: new Date().toISOString(),
      },
      {
        id: '2',
        vendor_ids: ['1', '3'],
        pattern_type: 'bid_rigging',
        confidence: 88,
        severity: 'critical',
        description: 'Suspicious pattern of rotating lowest bidders',
        detected_at: new Date().toISOString(),
      },
    ];
  }
}

export const vendorService = new VendorService();
