import { api } from './api';

export interface ProcurementSummary {
  totalCases: number;
  totalVendors: number;
  totalContracts: number;
  totalValue: number;
  highRiskVendors: number;
  collusionPatterns: number;
  integrityScore: number;
  monthlyTrend?: { month: string; value: number }[];
}

export interface CollusionPattern {
  id: string;
  type: string;
  description: string;
  confidence: number;
  severity: string;
  entities: string[];
  caseIds: string[];
  detectedAt: string;
}

class ProcurementApiService {
  async getSummary(): Promise<ProcurementSummary> {
    return {
      totalCases: 6,
      totalVendors: 4,
      totalContracts: 35,
      totalValue: 6500000000,
      highRiskVendors: 2,
      collusionPatterns: 3,
      integrityScore: 100,
      monthlyTrend: [
        { month: 'Jan', value: 1200000000 },
        { month: 'Feb', value: 950000000 },
        { month: 'Mar', value: 1500000000 },
        { month: 'Apr', value: 1800000000 },
        { month: 'May', value: 2100000000 },
        { month: 'Jun', value: 2500000000 }
      ]
    };
  }

  async getCollusionPatterns(): Promise<CollusionPattern[]> {
    return [
      {
        id: '1',
        type: 'Vendor Address Collusion',
        description: 'Multiple vendors sharing same registered address',
        confidence: 92,
        severity: 'high',
        entities: ['PT. Maju Jaya', 'CV. Karya Mandiri'],
        caseIds: ['case-001', 'case-002'],
        detectedAt: new Date().toISOString()
      },
      {
        id: '2',
        type: 'Bid Rigging Pattern',
        description: 'Rotating lowest bidders across multiple tenders',
        confidence: 88,
        severity: 'critical',
        entities: ['PT. Maju Jaya', 'PT. Bangun Nusantara'],
        caseIds: ['case-001', 'case-003'],
        detectedAt: new Date().toISOString()
      },
      {
        id: '3',
        type: 'Subcontractor Loop',
        description: 'Circular subcontracting between related parties',
        confidence: 75,
        severity: 'medium',
        entities: ['CV. Karya Mandiri', 'PT. Bangun Nusantara'],
        caseIds: ['case-002'],
        detectedAt: new Date().toISOString()
      }
    ];
  }
}

export const procurementApi = new ProcurementApiService();
