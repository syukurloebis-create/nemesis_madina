// Sidebar.tsx - Navigation Sidebar with RUP & Procurements
import React from 'react';
import { 
  LayoutDashboard, 
  Briefcase, 
  AlertTriangle, 
  Scale, 
  Shield, 
  Bot,
  Settings,
  LogOut,
  User,
  Bell,
  FileText,
  Building,
  Database
} from 'lucide-react';

interface MenuItem {
  id: string;
  label: string;
  icon: React.ReactNode;
  badge?: number;
}

interface SidebarProps {
  activeMenu: string;
  onMenuChange: (menuId: string) => void;
  items?: MenuItem[];
  onSettingsClick?: () => void;
  onLogoutClick?: () => void;
}

const defaultItems: MenuItem[] = [
  { id: 'dashboard', label: 'Dashboard', icon: <LayoutDashboard className="w-5 h-5" /> },
  { id: 'cases', label: 'Cases', icon: <Briefcase className="w-5 h-5" />, badge: 6 },
  { id: 'fraud', label: 'Fraud', icon: <AlertTriangle className="w-5 h-5" />, badge: 3 },
  { id: 'decisions', label: 'Decisions', icon: <Scale className="w-5 h-5" />, badge: 3 },
  { id: 'evidence', label: 'Evidence', icon: <Shield className="w-5 h-5" />, badge: 24 },
  { id: 'copilot', label: 'AI Copilot', icon: <Bot className="w-5 h-5" /> },
  { id: 'procurements', label: 'Procurements', icon: <Building className="w-5 h-5" />, badge: 10 },
];

export const Sidebar: React.FC<SidebarProps> = ({ 
  activeMenu, 
  onMenuChange,
  items = defaultItems,
  onSettingsClick,
  onLogoutClick
}) => {
  const handleSettings = () => {
    if (onSettingsClick) {
      onSettingsClick();
    } else {
      console.log('⚙️ Settings clicked');
      alert('⚙️ Settings - Coming soon!');
    }
  };

  const handleLogout = () => {
    if (onLogoutClick) {
      onLogoutClick();
    } else {
      console.log('🚪 Logout clicked');
      if (confirm('Apakah Anda yakin ingin keluar?')) {
        localStorage.clear();
        window.location.href = '/login';
      }
    }
  };

  return (
    <aside className="w-64 min-h-screen bg-dark-card border-r border-dark-border flex-shrink-0 flex flex-col">
      {/* Logo */}
      <div className="p-4 border-b border-dark-border">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-primary-500/10 border border-primary-500/20">
            <Bot className="w-5 h-5 text-primary-400" />
          </div>
          <span className="text-lg font-bold gradient-text">NEMESIS AI</span>
          <span className="text-xs text-dark-muted">v8.0</span>
        </div>
      </div>

      {/* User Info */}
      <div className="px-4 py-3 border-b border-dark-border">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-primary-500/20 flex items-center justify-center">
            <User className="w-4 h-4 text-primary-400" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-white truncate">Admin User</p>
            <p className="text-xs text-dark-muted truncate">super_admin</p>
          </div>
          <button className="p-1 text-dark-muted hover:text-white transition-colors relative">
            <Bell className="w-4 h-4" />
            <span className="absolute -top-0.5 -right-0.5 w-2 h-2 bg-red-500 rounded-full" />
          </button>
        </div>
      </div>

      {/* Menu */}
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        {items.map((item) => (
          <button
            key={item.id}
            onClick={() => onMenuChange(item.id)}
            className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-sm transition-all ${
              activeMenu === item.id
                ? 'bg-primary-500/10 text-primary-400 border border-primary-500/20'
                : 'text-dark-muted hover:text-white hover:bg-dark-bg'
            }`}
          >
            <div className="flex items-center gap-3">
              {item.icon}
              <span>{item.label}</span>
            </div>
            {item.badge !== undefined && item.badge > 0 && (
              <span className={`px-2 py-0.5 text-xs rounded-full ${
                activeMenu === item.id
                  ? 'bg-primary-500/20 text-primary-400'
                  : 'bg-dark-bg text-dark-muted'
              }`}>
                {item.badge}
              </span>
            )}
          </button>
        ))}
      </nav>

      {/* Footer Menu - Settings & Logout */}
      <div className="border-t border-dark-border p-3 space-y-1">
        <button
          onClick={handleSettings}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-dark-muted hover:text-white hover:bg-dark-bg transition-all"
        >
          <Settings className="w-5 h-5" />
          <span>Settings</span>
        </button>
        <button
          onClick={handleLogout}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-dark-muted hover:text-red-400 hover:bg-red-500/10 transition-all"
        >
          <LogOut className="w-5 h-5" />
          <span>Logout</span>
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
