import React from 'react';

interface MainLayoutProps {
  children: React.ReactNode;
}

/**
 * MainLayout — pure shell.
 *
 * Tab navigation is handled exclusively by IntelligenceTabs
 * (rendered by Dashboard as a child). This component only
 * provides the header + content container.
 *
 * Phase D.5: removed duplicate 9-tab navigation block that was
 * non-functional (no activeTab/onTabChange props passed by Dashboard).
 */
export const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen bg-gray-900">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700 px-6 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold">N</span>
            </div>
            <h1 className="text-xl font-bold text-white">NEMESIS</h1>
            <span className="text-xs text-gray-500 ml-2">v8.1</span>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-400">System: Operational</span>
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="p-6">
        {children}
      </main>
    </div>
  );
};

export default MainLayout;
