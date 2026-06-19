import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuthStore } from './stores/authStore';
import useWebSocket from './hooks/useWebSocket';
import { 
  LayoutDashboard, 
  AlertTriangle, 
  Users, 
  History, 
  GitBranch, 
  Shield, 
  FolderOpen,
  ShoppingBag,
  FileText,
  Menu,
  X,
  Search,
  Bell,
  User,
  LogOut,
  Wifi,
  WifiOff
} from 'lucide-react';
import { SearchBar } from './components/common/SearchBar';

const navItems = [
  { path: '/', icon: LayoutDashboard, label: 'Dashboard Eksekutif' },
  { path: '/threat-center', icon: AlertTriangle, label: 'Pusat Ancaman' },
  { path: '/entity', icon: Users, label: 'Ruang Kerja Entitas' },
  { path: '/temporal-replay', icon: History, label: 'Pemutaran Temporal' },
  { path: '/graph-intelligence', icon: GitBranch, label: 'Intelijen Graf' },
  { path: '/governance', icon: Shield, label: 'Pusat Tata Kelola' },
  { path: '/investigation', icon: FolderOpen, label: 'Kasus Investigasi' },
  { path: '/procurement-intelligence', icon: ShoppingBag, label: 'Intelijen Pengadaan' },
  { path: '/audit-trail', icon: FileText, label: 'Jejak Audit' },
  { path: '/integrated-dashboard', icon: LayoutDashboard, label: 'Dashboard Terintegrasi' },
];

export const WorkspaceLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const location = useLocation();
  const navigate = useNavigate();
  
  const { user, token, logout, isAuthenticated } = useAuthStore();
  
  const { connected, authError } = useWebSocket(
    `/ws/${user?.id || 'workspace'}`,
    {
      autoConnect: !!token && isAuthenticated(),
      onMessage: (msg) => {
        console.log('📡 Real-time update:', msg);
      },
    }
  );

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate('/login');
    }
  }, [isAuthenticated, navigate]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="flex min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-black">
      {/* Sidebar */}
      <aside className={`${sidebarOpen ? 'w-64' : 'w-20'} bg-gray-900/95 border-r border-cyan-500/30 transition-all duration-300 flex flex-col fixed h-full z-30`}>
        <div className="p-4 border-b border-gray-800 flex items-center justify-between">
          <div className={`${!sidebarOpen && 'hidden'}`}>
            <h1 className="text-lg font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">NEMESIS V8+</h1>
            <p className="text-xs text-gray-500">Forensic Intelligence</p>
          </div>
          <button onClick={() => setSidebarOpen(!sidebarOpen)} className="p-1 hover:bg-gray-800 rounded">
            {sidebarOpen ? <X className="w-5 h-5 text-gray-400" /> : <Menu className="w-5 h-5 text-gray-400" />}
          </button>
        </div>

        {/* WebSocket Status */}
        <div className={`px-4 py-2 border-b border-gray-800 ${!sidebarOpen && 'text-center'}`}>
          <div className="flex items-center gap-2">
            {connected ? (
              <>
                <Wifi className="w-3 h-3 text-green-400" />
                <span className={`text-xs text-green-400 ${!sidebarOpen && 'hidden'}`}>Live</span>
              </>
            ) : authError ? (
              <>
                <WifiOff className="w-3 h-3 text-red-400" />
                <span className={`text-xs text-red-400 ${!sidebarOpen && 'hidden'}`}>Auth Error</span>
              </>
            ) : (
              <>
                <WifiOff className="w-3 h-3 text-yellow-500" />
                <span className={`text-xs text-yellow-500 ${!sidebarOpen && 'hidden'}`}>Connecting...</span>
              </>
            )}
          </div>
        </div>

        <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path || 
              (item.path === '/entity' && location.pathname.startsWith('/entity'));
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-4 py-2 rounded-lg transition-all ${
                  isActive 
                    ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30' 
                    : 'text-gray-400 hover:bg-gray-800 hover:text-white'
                }`}
              >
                <Icon className="w-5 h-5" />
                <span className={`${!sidebarOpen && 'hidden'} text-sm`}>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        <div className="p-4 border-t border-gray-800">
          <div className="flex items-center gap-3">
            <div className="relative">
              <User className="w-8 h-8 p-1.5 bg-gray-800 rounded-full text-gray-400" />
              {connected && (
                <span className="absolute bottom-0 right-0 w-2 h-2 bg-green-400 rounded-full" />
              )}
            </div>
            <div className={`${!sidebarOpen && 'hidden'} flex-1`}>
              <div className="text-sm font-medium text-white truncate">
                {user?.full_name || user?.username || 'Investigator'}
              </div>
              <div className="text-xs text-gray-500">{user?.role || 'Forensic Analyst'}</div>
              <div className="text-xs text-gray-600 truncate">{user?.institution_id}</div>
            </div>
            <button
              onClick={handleLogout}
              className={`p-1.5 hover:bg-gray-800 rounded-lg transition-colors ${!sidebarOpen && 'mx-auto'}`}
              title="Logout"
            >
              <LogOut className="w-4 h-4 text-gray-400 hover:text-red-400" />
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className={`flex-1 ${sidebarOpen ? 'ml-64' : 'ml-20'} transition-all duration-300`}>
        {/* Top Bar */}
        <div className="sticky top-0 z-20 bg-gray-900/80 backdrop-blur border-b border-gray-800 px-6 py-3 flex items-center justify-between">
          <SearchBar />
          
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 px-3 py-1 bg-gray-800 rounded-lg">
              {connected ? (
                <>
                  <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                  <span className="text-xs text-green-400">REALTIME</span>
                </>
              ) : (
                <>
                  <div className="w-2 h-2 bg-gray-500 rounded-full" />
                  <span className="text-xs text-gray-500">RECONNECTING</span>
                </>
              )}
            </div>
            
            <button className="relative p-2 hover:bg-gray-800 rounded-lg transition-colors">
              <Bell className="w-5 h-5 text-gray-400" />
              <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
            </button>
            
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse" />
              <span className="text-sm text-cyan-400">AI ACTIVE</span>
            </div>
          </div>
        </div>

        {/* Page Content */}
        <div className="p-6">
          {children}
        </div>
      </main>
    </div>
  );
};
