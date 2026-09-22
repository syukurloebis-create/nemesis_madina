import React, { useState } from 'react';
import { IntelligenceModel } from '../../services/intelligenceAdapter';
import OverviewTab from '../dashboard/OverviewTab';
import RiskReasoningPanel from './RiskReasoningPanel';
import GraphIntelligence from '../graph/GraphIntelligence';
import FraudSignalExplorer from './FraudSignalExplorer';
import EvidenceHealthPanel from './EvidenceHealthPanel';
import InvestigationTimeline from './InvestigationTimeline';
import InvestigationWorkspace from '../investigation/InvestigationWorkspace';
import RecoveryIntelligence from '../../pages/RecoveryIntelligence';
import type {
  DashboardActionId,
  IntelligenceTabId,
} from '../../types/navigation';
// import DecisionCenter from '../decision/DecisionCenter';

interface Props {
  intelligence: IntelligenceModel;
  activeTab: IntelligenceTabId;
  setActiveTab: (tab: IntelligenceTabId) => void;
  caseId: string;
  userId?: string;
  onAction?: (action: DashboardActionId) => void;
}

export default function IntelligenceTabs({ 
  intelligence, 
  activeTab, 
  setActiveTab,
  caseId,
  userId = '',
  onAction 
}: Props) {
  const tabs: Array<{ id: IntelligenceTabId; label: string }> = [
    { id: 'overview', label: 'Overview' },
    { id: 'risk', label: 'Risk Reasoning' },
    { id: 'graph', label: 'Graph Intelligence' },
    { id: 'fraud', label: 'Fraud Signals' },
    { id: 'evidence', label: 'Evidence Health' },
    { id: 'timeline', label: 'Investigation Timeline' },
    { id: 'investigation', label: 'Investigation' },
    // { id: 'decisions', label: 'Decisions' },
    { id: 'recovery', label: 'Recovery' },
  ];

  return (
    <div className="space-y-4">
      {/* Tab Navigation */}
      <div className="flex flex-wrap gap-2 border-b border-gray-700 pb-2">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
              activeTab === tab.id
                ? 'bg-blue-600 text-white'
                : 'text-gray-400 hover:text-white hover:bg-gray-800'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="min-h-[400px]">
        {activeTab === 'overview' && (
          <OverviewTab intelligence={intelligence} onAction={onAction} />
        )}
        {activeTab === 'risk' && (
          <RiskReasoningPanel caseId={caseId} />
        )}
        {activeTab === 'graph' && (
          <GraphIntelligence caseId={caseId} intelligence={intelligence} />
        )}
        {activeTab === 'fraud' && (
          <FraudSignalExplorer intelligence={intelligence} />
        )}
        {activeTab === 'evidence' && (
          <EvidenceHealthPanel intelligence={intelligence} />
        )}
        {activeTab === 'timeline' && (
          <InvestigationTimeline intelligence={intelligence} />
        )}
        {activeTab === 'investigation' && (
          <InvestigationWorkspace caseId={caseId} />
        )}
        {/* {activeTab === 'decisions' && (
          <DecisionCenter caseId={caseId} userId={userId} />
        )} */}
        {activeTab === 'recovery' && (
          <RecoveryIntelligence />
        )}
      </div>
    </div>
  );
}
