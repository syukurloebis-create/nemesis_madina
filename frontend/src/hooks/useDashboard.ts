import { useQuery } from '@tanstack/react-query';
import { getExecutiveOverview, getEvidenceStats, getGovernanceMetrics, getKeyActors, getCommunities } from '../api/nemesisApi';
import { getKeyActors } from '../services/api';

export const useExecutiveOverview = () => {
  return useQuery({
    queryKey: ['executiveOverview'],
    queryFn: async () => {
      const res = await getExecutiveOverview();
      return res.data;
    },
  });
};

export const useEvidenceStats = () => {
  return useQuery({
    queryKey: ['evidenceStats'],
    queryFn: async () => {
      const res = await getEvidenceStats();
      return res.data;
    },
  });
};

export const useGovernanceMetrics = () => {
  return useQuery({
    queryKey: ['governanceMetrics'],
    queryFn: async () => {
      const res = await getGovernanceMetrics();
      return res.data;
    },
  });
};

export const useKeyActors = () => {
  return useQuery({
    queryKey: ['keyActors'],
    queryFn: async () => {
      const res = await getKeyActors();
      return res.data;
    },
  });
};

export const useCommunities = () => {
  return useQuery({
    queryKey: ['communities'],
    queryFn: async () => {
      const res = await getCommunities();
      return res.data;
    },
  });
};
