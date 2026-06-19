// MainLayout.tsx - Main Layout with Sidebar
import React from 'react';
import Sidebar from './Sidebar';

interface MainLayoutProps {
  children: React.ReactNode;
  activeMenu?: string;
  onMenuChange?: (menuId: string) => void;
  onSettingsClick?: () => void;
  onLogoutClick?: () => void;
}

export const MainLayout: React.FC<MainLayoutProps> = ({ 
  children, 
  activeMenu = 'dashboard', 
  onMenuChange = () => {},
  onSettingsClick,
  onLogoutClick
}) => {
  return (
    <div className="flex min-h-screen bg-dark-bg">
      <Sidebar 
        activeMenu={activeMenu} 
        onMenuChange={onMenuChange}
        onSettingsClick={onSettingsClick}
        onLogoutClick={onLogoutClick}
      />
      <main className="flex-1 overflow-auto">
        {children}
      </main>
    </div>
  );
};

export default MainLayout;
