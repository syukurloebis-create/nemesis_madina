export interface Vendor {
  id: string;
  name: string;
  registration_number: string;
  tax_id: string;
  address: string;
  city: string;
  province: string;
  postal_code: string;
  phone: string;
  email: string;
  website: string;
  established_year: number;
  business_type: string;
  classification: 'small' | 'medium' | 'large';
  risk_score: number;
  risk_level: 'critical' | 'high' | 'medium' | 'low';
  status: 'active' | 'suspended' | 'blacklisted';
  related_cases: number;
  total_contracts: number;
  total_value: number;
  last_audit: string;
  created_at: string;
  updated_at: string;
  metadata: Record<string, any>;
}

export interface VendorContract {
  id: string;
  vendor_id: string;
  contract_number: string;
  title: string;
  value: number;
  start_date: string;
  end_date: string;
  status: 'active' | 'completed' | 'terminated';
  case_id?: string;
}

export interface VendorCollusion {
  id: string;
  vendor_ids: string[];
  pattern_type: 'address' | 'bid_rigging' | 'subcontractor' | 'conflict';
  confidence: number;
  severity: 'critical' | 'high' | 'medium' | 'low';
  description: string;
  detected_at: string;
  case_id?: string;
}

export interface VendorRiskFactor {
  id: string;
  vendor_id: string;
  factor: string;
  weight: number;
  description: string;
  detected_at: string;
}

// Export all types as default for convenience
export type VendorTypes = {
  Vendor: Vendor;
  VendorContract: VendorContract;
  VendorCollusion: VendorCollusion;
  VendorRiskFactor: VendorRiskFactor;
};
