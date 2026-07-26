import { investigationsApi } from '../api';

export interface Investigation {
  id: string;
  case_id: string;
  title: string;
  status: string;
  priority: string;
  assigned_to?: string;
  created_at: string;
  updated_at: string;
}

export const investigationService = {
  getByCase: (caseId: string) => investigationsApi.getByCase(caseId),
  getStats: (caseId: string) => investigationsApi.getStats(caseId),
  updateStatus: (id: string, status: string, progress?: number) => 
    investigationsApi.updateStatus(id, status, progress),
  escalate: (id: string, reason: string, target_level?: string) => 
    investigationsApi.escalate(id, reason, target_level),
  addNote: (id: string, note: string) => 
    investigationsApi.addNote(id, note),
};

// Alias untuk kompatibilitas
export const investigationsService = investigationService;

export default investigationService;
