import React, { createContext, useContext, ReactNode } from 'react';
import { useIntelligenceDashboard } from '@/hooks/useIntelligenceDashboard';
import { DashboardData } from '@/types/dashboard';

interface DashboardContextType {
  data: DashboardData | null;
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
  isStale: boolean;
}

const DashboardContext = createContext<DashboardContextType | undefined>(undefined);

interface DashboardProviderProps {
  children: ReactNode;
  caseId: string;
}

export const DashboardProvider: React.FC<DashboardProviderProps> = ({ 
  children, 
  caseId 
}) => {
  const dashboard = useIntelligenceDashboard(caseId);
  
  return (
    <DashboardContext.Provider value={dashboard}>
      {children}
    </DashboardContext.Provider>
  );
};

export const useDashboard = (): DashboardContextType => {
  const context = useContext(DashboardContext);
  if (!context) {
    throw new Error('useDashboard must be used within DashboardProvider');
  }
  return context;
};

export default DashboardContext;
