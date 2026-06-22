// src/services/evidenceApi.ts
import api from './api';
import type { Evidence, EvidenceStats, CustodyRecord } from '../types';

const evidenceApi = {
  getEvidence: (caseId: string) => {
    return api.get<Evidence[]>(`/api/v1/evidence/case/${caseId}`);
  },
  getEvidenceById: (evidenceId: string) => {
    return api.get<Evidence>(`/api/v1/evidence/${evidenceId}`);
  },
  getEvidenceStats: () => {
    return api.get<EvidenceStats>('/api/v1/evidence/stats');
  },
  uploadEvidence: (caseId: string, file: File, metadata?: Record<string, any>) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('case_id', caseId);
    if (metadata) {
      formData.append('metadata', JSON.stringify(metadata));
    }
    return api.post<Evidence>('/api/v1/evidence/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  verifyEvidence: (evidenceId: string) => {
    return api.post<Evidence>(`/api/v1/evidence/${evidenceId}/verify`);
  },
  getCustodyHistory: (evidenceId: string) => {
    return api.get<CustodyRecord[]>(`/api/v1/evidence/${evidenceId}/custody`);
  },
  getTopEvidence: (limit: number = 10) => {
    return api.get<Evidence[]>(`/api/v1/evidence/top?limit=${limit}`);
  },
};

export default evidenceApi;
