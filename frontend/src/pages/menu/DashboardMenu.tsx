// src/pages/menu/DashboardMenu.tsx - CLEAN VERSION
import React from 'react';
import { useDashboardData } from '../../hooks/useDashboardData';
import { AIStatusBar } from '../../components/intelligence/AIStatusBar';
import { AIRiskScore } from '../../components/intelligence/AIRiskScore';
import IntelligenceKPICards from '../../components/intelligence/IntelligenceKPICards';
import { EnhancedNetworkGraph } from '../../components/network/EnhancedNetworkGraph';

// ============ KOMPONEN BARU ============
import { HighRiskPackages } from '../../components/dashboard/HighRiskPackages';
import { SharedPackageDetail } from '../../components/fraud/SharedPackageDetail';
import { CollusionIndicators } from '../../components/fraud/CollusionIndicators';

interface Props {
  caseId: string;
  evidenceId: string;
}

export const DashboardMenu: React.FC<Props> = ({ caseId, evidenceId }) => {
  const { loading, error, data, refetch } = useDashboardData(caseId);

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p className="mt-4 text-gray-400">Memuat data dashboard...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-500/10 border border-red-500/30 p-6 rounded-xl text-red-400">
        <p className="font-semibold">⚠️ Error Memuat Dashboard</p>
        <p className="text-sm mt-2">{error}</p>
        <button
          onClick={() => refetch()}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition"
        >
          🔄 Coba Lagi
        </button>
      </div>
    );
  }

  const { strategic, keyActors, intelligence, graphRisk } = data || {
    strategic: null,
    keyActors: [],
    intelligence: null,
    graphRisk: null,
  };

  return (
    <div className="space-y-6">
      {/* AI Status Bar */}
      <AIStatusBar 
        isActive={!!intelligence}
        lastUpdate={intelligence?.timestamp || new Date().toISOString()}
      />

      {/* Intelligence KPICards */}
      {intelligence && (
        <IntelligenceKPICards
          riskScore={intelligence.risk_score}
          riskLevel={intelligence.risk_level}
          components={intelligence.components}
        />
      )}

      {/* AI Risk Score */}
      {intelligence && graphRisk && (
        <AIRiskScore
          intelligence={intelligence}
          graphRisk={graphRisk}
          caseId={caseId}
        />
      )}

      {/* ============ KOMPONEN BARU ============ */}
      
      {/* 1. HIGH RISK PACKAGES */}
      <HighRiskPackages caseId={caseId} />

      {/* 2. SHARED PACKAGE DETAIL */}
      <SharedPackageDetail caseId={caseId} />

      {/* 3. COLLUSION INDICATORS */}
      <CollusionIndicators caseId={caseId} />

      {/* Strategic Dashboard */}
      {strategic && (
        <div className="bg-dark-card rounded-xl shadow-lg border border-gray-700/50 p-6">
          <h3 className="text-lg font-semibold text-white mb-4">📊 Ringkasan Strategis</h3>
          <pre className="text-xs text-gray-400 overflow-auto max-h-60">
            {JSON.stringify(strategic, null, 2)}
          </pre>
        </div>
      )}

      {/* Network Graph */}
      {keyActors && keyActors.length > 0 && (
        <div className="bg-dark-card rounded-xl shadow-lg border border-gray-700/50 p-6">
          <h3 className="text-lg font-semibold text-white mb-4">🌐 Jaringan Aktor Kunci</h3>
          <EnhancedNetworkGraph data={keyActors} />
        </div>
      )}

      {/* Intelligence Metadata */}
      {intelligence && (
        <div className="text-xs text-gray-500 text-right border-t border-gray-700/50 pt-4 mt-4">
          <p>Kasus: {intelligence.case_id}</p>
          <p>Versi: {intelligence.version}</p>
          <p>Diperbarui: {new Date(intelligence.timestamp).toLocaleString('id-ID')}</p>
        </div>
      )}
    </div>
  );
};

export default DashboardMenu;
