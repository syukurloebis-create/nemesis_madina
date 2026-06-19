// NEMESIS AI COMMAND CENTER
import React, { useState } from 'react';
import { MainLayout } from '../components/layout/MainLayout';
import { useDashboardData } from '../hooks/useDashboardData';

import { DashboardMenu } from './menu/DashboardMenu';
import { CasesMenu } from './menu/CasesMenu';
import { FraudMenu } from './menu/FraudMenu';
import { DecisionsMenu } from './menu/DecisionsMenu';
import { EvidenceMenu } from './menu/EvidenceMenu';
import { CopilotMenu } from './menu/CopilotMenu';
import { ProcurementsMenu } from './menu/ProcurementsMenu';
import { SystemStatus } from '../components/observability/SystemStatus';

export const Dashboard: React.FC = () => {
  const [activeMenu, setActiveMenu] = useState('dashboard');
  const [selectedCaseId] = useState('446e216d-eb0e-487e-8e6b-ec943468ea20');
  const [selectedEvidenceId] = useState('7718c76d-edf8-4155-acb6-b4a39cf7a136');

  const handleSettings = () => {
    alert('⚙️ Settings - Coming soon!');
  };

  const handleLogout = () => {
    if (window.confirm('Apakah Anda yakin ingin keluar?')) {
      localStorage.clear();
      window.location.href = '/login';
    }
  };

  const renderContent = () => {
    switch (activeMenu) {
      case 'dashboard':
        return <DashboardMenu caseId={selectedCaseId} evidenceId={selectedEvidenceId} />;
      case 'cases':
        return <CasesMenu caseId={selectedCaseId} />;
      case 'fraud':
        return <FraudMenu onInvestigate={(id) => console.log('Investigating:', id)} />;
      case 'decisions':
        return <DecisionsMenu caseId={selectedCaseId} />;
      case 'evidence':
        return <EvidenceMenu evidenceId={selectedEvidenceId} />;
      case 'copilot':
        return <CopilotMenu />;
      case 'procurements':
        return <ProcurementsMenu />;
      default:
        return <DashboardMenu caseId={selectedCaseId} evidenceId={selectedEvidenceId} />;
    }
  };

  return (
    <div className="min-h-screen bg-dark-bg text-white">
      <MainLayout 
        activeMenu={activeMenu} 
        onMenuChange={setActiveMenu}
        onSettingsClick={handleSettings}
        onLogoutClick={handleLogout}
      >
        <div className="p-6">
          {renderContent()}
        </div>
      </MainLayout>
      <SystemStatus />
    </div>
  );
};

export default Dashboard;
