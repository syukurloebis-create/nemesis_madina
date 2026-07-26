import React from 'react';

interface MainLayoutProps {
  children: React.ReactNode;
  activeTab?: string;
  onTabChange?: (tab: string) => void;
}

export const MainLayout: React.FC<MainLayoutProps> = ({ 
  children, 
  activeTab = 'overview',
  onTabChange 
}) => {
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

      {/* Tab Navigation */}
      <div className="border-b border-gray-700 px-6">
        <div className="flex gap-1 overflow-x-auto">
          {['overview', 'risk-reasoning', 'investigation', 'recommendations', 'decisions', 'alerts', 'procurement', 'vendors', 'recovery'].map((tab) => (
            <button
              key={tab}
              onClick={() => onTabChange?.(tab)}
              className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                activeTab === tab
                  ? 'border-blue-500 text-white'
                  : 'border-transparent text-gray-400 hover:text-gray-200 hover:border-gray-600'
              }`}
            >
              {{
                overview: 'Overview',
                'risk-reasoning': 'Risk Reasoning',
                investigation: 'Investigation',
                recommendations: 'Recommendations',
                decisions: 'Decisions',
                alerts: 'Alerts',
                procurement: 'Procurement Intelligence',
                vendors: 'Vendor Intelligence',
                recovery: 'Recovery Intelligence'
              }[tab]}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <main className="p-6">
        {children}
      </main>
    </div>
  );
};

export default MainLayout;
