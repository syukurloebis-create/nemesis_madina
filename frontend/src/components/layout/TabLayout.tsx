// TabLayout.tsx - Tab-based navigation untuk detail content
import React, { useState } from 'react';
import { 
  Briefcase, 
  Scale, 
  Shield, 
  Bot,
  TrendingUp,
  AlertTriangle
} from 'lucide-react';

interface Tab {
  id: string;
  label: string;
  icon: React.ReactNode;
  badge?: number;
  component: React.ReactNode;
}

interface TabLayoutProps {
  tabs: Tab[];
  defaultTab?: string;
  className?: string;
}

export const TabLayout: React.FC<TabLayoutProps> = ({
  tabs,
  defaultTab,
  className = ''
}) => {
  const [activeTab, setActiveTab] = useState(defaultTab || tabs[0]?.id || '');

  const activeComponent = tabs.find(t => t.id === activeTab)?.component;

  return (
    <div className={`glass-card ${className}`}>
      {/* Tab Navigation */}
      <div className="flex border-b border-dark-border overflow-x-auto">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-4 py-3 text-sm font-medium transition-all border-b-2 whitespace-nowrap ${
              activeTab === tab.id
                ? 'border-primary-500 text-primary-400'
                : 'border-transparent text-dark-muted hover:text-white hover:border-dark-border'
            }`}
          >
            {tab.icon}
            {tab.label}
            {tab.badge !== undefined && tab.badge > 0 && (
              <span className="ml-1 px-2 py-0.5 text-xs rounded-full bg-primary-500/20 text-primary-400">
                {tab.badge}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="p-4 max-h-[500px] overflow-y-auto dark-scrollbar">
        {activeComponent || <p className="text-dark-muted">No content</p>}
      </div>
    </div>
  );
};

export default TabLayout;
