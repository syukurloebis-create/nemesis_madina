// src/components/dashboard/DashboardLayout.tsx
import React, { useState } from 'react';

interface DashboardLayoutProps {
  children: React.ReactNode;
  activeTab: string;
  onTabChange: (tab: string) => void;
}

const menuItems = [
  { id: 'executive', label: '📊 Executive', icon: '📊' },
  { id: 'fraud', label: '🔍 Fraud', icon: '🔍' },
  { id: 'cases', label: '📋 Cases', icon: '📋' },
  { id: 'evidence', label: '📄 Evidence', icon: '📄' },
  { id: 'decision', label: '💡 Decision', icon: '💡' },
  { id: 'early-warning', label: '🚨 Early Warning', icon: '🚨' },
  { id: 'graph', label: '🌐 Graph', icon: '🌐' },
  { id: 'rup', label: '🏢 RUP', icon: '🏢' },
  { id: 'system', label: '⚙️ System', icon: '⚙️' },
];

export const DashboardLayout: React.FC<DashboardLayoutProps> = ({
  children,
  activeTab,
  onTabChange,
}) => {
  const [collapsed, setCollapsed] = useState(false);

  const handleTabChange = (tabId: string) => {
    if (onTabChange && typeof onTabChange === 'function') {
      onTabChange(tabId);
    }
  };

  return (
    <div className="flex h-screen bg-dark-bg text-white overflow-hidden">
      {/* SIDEBAR */}
      <aside className={`${collapsed ? 'w-16' : 'w-56'} bg-dark-card border-r border-gray-700/50 flex-shrink-0 transition-all duration-300 flex flex-col`}>
        <div className="p-3 border-b border-gray-700/50 flex items-center gap-2">
          <div className="w-7 h-7 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold text-xs flex-shrink-0">N</div>
          {!collapsed && (
            <div className="flex-1 min-w-0">
              <h1 className="text-white font-bold text-sm leading-none">NEMESIS</h1>
              <p className="text-[8px] text-gray-500">v8.0.0 · Strategic Intel</p>
            </div>
          )}
          <button onClick={() => setCollapsed(!collapsed)} className="text-gray-400 hover:text-white text-xs">
            {collapsed ? '→' : '←'}
          </button>
        </div>

        <div className="p-3 border-b border-gray-700/50">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-full bg-blue-600/20 flex items-center justify-center text-blue-400 text-xs font-bold">A</div>
            {!collapsed && (
              <div className="flex-1 min-w-0">
                <p className="text-xs text-white font-medium">Admin User</p>
                <p className="text-[10px] text-gray-500">super_admin</p>
              </div>
            )}
          </div>
        </div>

        <nav className="flex-1 overflow-y-auto p-2 space-y-0.5">
          {menuItems.map((item) => (
            <button
              key={item.id}
              onClick={() => handleTabChange(item.id)}
              className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg transition-colors text-xs ${
                activeTab === item.id
                  ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30'
                  : 'text-gray-400 hover:text-white hover:bg-gray-800/50'
              }`}
            >
              <span className="text-sm">{item.icon}</span>
              {!collapsed && <span className="whitespace-nowrap">{item.label}</span>}
            </button>
          ))}
        </nav>

        <div className="p-2 border-t border-gray-700/50 text-[8px] text-gray-600 text-center">
          {!collapsed ? '© 2026 NEMESIS AI' : '©'}
        </div>
      </aside>

      {/* MAIN CONTENT */}
      <main className="flex-1 flex flex-col overflow-hidden">
        <header className="bg-dark-card border-b border-gray-700/50 flex-shrink-0 px-4 py-2">
          <div className="flex gap-1 overflow-x-auto">
            {menuItems.map((item) => (
              <button
                key={item.id}
                onClick={() => handleTabChange(item.id)}
                className={`px-3 py-1.5 text-xs font-medium rounded-t-lg transition-colors whitespace-nowrap flex-shrink-0 ${
                  activeTab === item.id
                    ? 'bg-blue-600/20 text-blue-400 border-b-2 border-blue-500'
                    : 'text-gray-400 hover:text-white hover:bg-gray-800/50'
                }`}
              >
                {item.label}
              </button>
            ))}
          </div>
        </header>

        <div className="flex-1 overflow-auto p-4 md:p-6">
          {children}
        </div>
      </main>
    </div>
  );
};
