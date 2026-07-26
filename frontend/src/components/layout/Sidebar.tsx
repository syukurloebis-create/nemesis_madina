import React, { useState } from 'react';
import {
  LayoutDashboard,
  Brain,
  Search,
  Lightbulb,
  Scale,
  Bell,
  Package,
  Users,
  Settings,
  LogOut,
  ChevronLeft,
  ChevronRight,
  Home,
  TrendingUp,
  Shield,
  FileText,
} from 'lucide-react';
import {
  ...
  RotateCcw,
} from 'lucide-react';

interface SidebarProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

interface NavItem {
  id: string;
  label: string;
  icon: React.ReactNode;
  badge?: number;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  onTabChange,
  isCollapsed,
  onToggleCollapse,
}) => {
  const [isHovered, setIsHovered] = useState(false);

  const navItems: NavItem[] = [
    { 
      id: 'overview', 
      label: 'Overview', 
      icon: <LayoutDashboard className="w-5 h-5" /> 
    },

    { 
      id: 'risk-reasoning', 
      label: 'Risk Reasoning', 
      icon: <Brain className="w-5 h-5" /> 
    },

    { 
      id: 'investigation', 
      label: 'Investigation', 
      icon: <Search className="w-5 h-5" /> 
    },

    { 
      id: 'recommendations', 
      label: 'Recommendations', 
      icon: <Lightbulb className="w-5 h-5" />,
      badge:5
    },

    { 
      id: 'decisions', 
      label: 'Decisions', 
      icon: <Scale className="w-5 h-5" />,
      badge:3
    },

    { 
      id: 'alerts', 
      label: 'Alerts', 
      icon: <Bell className="w-5 h-5" />,
      badge:5
    },

    { 
      id: 'procurement', 
      label: 'Procurement', 
      icon: <Package className="w-5 h-5" /> 
    },

    { 
      id: 'vendors', 
      label: 'Vendors', 
      icon: <Users className="w-5 h-5" /> 
    },

    {
      id:'recovery',
      label:'Recovery Intelligence',
      icon:<RotateCcw className="w-5 h-5" />
    }
  ];

  const bottomItems: NavItem[] = [
    { id: 'settings', label: 'Settings', icon: <Settings className="w-5 h-5" /> },
  ];

  const isExpanded = !isCollapsed || isHovered;

  return (
    <div
      className={`h-screen bg-dark-card border-r border-dark-border flex flex-col transition-all duration-300 ${
        isExpanded ? 'w-64' : 'w-20'
      }`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Logo */}
      <div className="p-4 border-b border-dark-border flex items-center justify-between">
        {isExpanded ? (
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-lg bg-primary-500/10 border border-primary-500/20">
              <Shield className="w-6 h-6 text-primary-400" />
            </div>
            <div>
              <span className="text-lg font-bold gradient-text">NEMESIS</span>
              <span className="text-xs text-dark-muted block">v8.0</span>
            </div>
          </div>
        ) : (
          <div className="p-2 rounded-lg bg-primary-500/10 border border-primary-500/20 mx-auto">
            <Shield className="w-6 h-6 text-primary-400" />
          </div>
        )}
        <button
          onClick={onToggleCollapse}
          className="p-1 rounded hover:bg-dark-hover text-dark-muted hover:text-white transition-colors"
        >
          {isExpanded ? <ChevronLeft className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        {navItems.map((item) => (
          <button
            key={item.id}
            onClick={() => onTabChange(item.id)}
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all ${
              activeTab === item.id
                ? 'bg-primary-500/10 text-primary-400 border border-primary-500/20'
                : 'text-dark-muted hover:text-white hover:bg-dark-hover'
            } ${!isExpanded ? 'justify-center' : ''}`}
          >
            <span className="flex-shrink-0">{item.icon}</span>
            {isExpanded && (
              <span className="flex-1 text-left">{item.label}</span>
            )}
            {isExpanded && item.badge && (
              <span className="px-2 py-0.5 text-xs font-medium bg-red-500/20 text-red-400 rounded-full">
                {item.badge}
              </span>
            )}
          </button>
        ))}
      </nav>

      {/* Bottom */}
      <div className="p-3 border-t border-dark-border space-y-1">
        {bottomItems.map((item) => (
          <button
            key={item.id}
            className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all text-dark-muted hover:text-white hover:bg-dark-hover ${
              !isExpanded ? 'justify-center' : ''
            }`}
          >
            <span className="flex-shrink-0">{item.icon}</span>
            {isExpanded && <span className="flex-1 text-left">{item.label}</span>}
          </button>
        ))}
        <button
          className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all text-red-400 hover:bg-red-500/10 ${
            !isExpanded ? 'justify-center' : ''
          }`}
        >
          <LogOut className="w-5 h-5 flex-shrink-0" />
          {isExpanded && <span className="flex-1 text-left">Logout</span>}
        </button>
      </div>
    </div>
  );
};

export default Sidebar;
