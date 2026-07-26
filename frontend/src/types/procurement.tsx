export type ProcurementStatus = 'planning' | 'tendering' | 'contract' | 'completed' | 'cancelled';

export interface ProcurementPackage {
  id: string;
  package_name: string;
  budget: number;
  budget_year: number;
  procurement_method: string;
  status: ProcurementStatus;
  vendor_id?: string;
  vendor_name?: string;
  contract_number?: string;
  contract_value?: number;
  start_date?: string;
  end_date?: string;
  risk_score?: number;
  risk_level?: string;
  created_at: string;
  updated_at: string;
}

export interface ProcurementStats {
  total_packages: number;
  total_budget: number;
  total_contract_value: number;
  avg_risk_score: number;
  by_status: Record<string, number>;
  by_method: Record<string, number>;
}
