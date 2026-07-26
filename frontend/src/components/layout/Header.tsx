import React, { useState } from 'react';
import { Search, Bell, User, Settings, Sun, Moon } from 'lucide-react';

export const Header: React.FC = () => {
  const [isDark, setIsDark] = useState(true);

  return (
    <header className="bg-dark-card border-b border-dark-border px-6 py-3 flex items-center justify-between">
      {/* Search */}
      <div className="flex-1 max-w-md">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-dark-muted" />
          <input
            type="text"
            placeholder="Search cases, vendors, entities..."
            className="w-full pl-10 pr-4 py-2 bg-dark-bg border border-dark-border rounded-lg text-white placeholder-dark-muted focus:outline-none focus:border-primary-500"
          />
        </div>
      </div>

      {/* Right side */}
      <div className="flex items-center gap-4">
        <button className="p-2 rounded-lg hover:bg-dark-hover text-dark-muted hover:text-white transition-colors relative">
          <Bell className="w-5 h-5" />
          <span className="absolute -top-1 -right-1 w-2 h-2 bg-red-500 rounded-full" />
        </button>
        <button
          onClick={() => setIsDark(!isDark)}
          className="p-2 rounded-lg hover:bg-dark-hover text-dark-muted hover:text-white transition-colors"
        >
          {isDark ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
        </button>
        <button className="p-2 rounded-lg hover:bg-dark-hover text-dark-muted hover:text-white transition-colors">
          <Settings className="w-5 h-5" />
        </button>
        <div className="flex items-center gap-2 pl-4 border-l border-dark-border">
          <div className="w-8 h-8 rounded-full bg-primary-500/20 flex items-center justify-center">
            <User className="w-4 h-4 text-primary-400" />
          </div>
          <div className="hidden md:block">
            <p className="text-sm font-medium text-white">Admin User</p>
            <p className="text-xs text-dark-muted">super_admin</p>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
