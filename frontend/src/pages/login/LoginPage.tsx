// LoginPage.tsx - Simple Login Page
import React, { useState } from 'react';
import { Bot, User, Lock, LogIn } from 'lucide-react';

export const LoginPage: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // Validasi sederhana
    if (!username || !password) {
      setError('Username dan password harus diisi');
      setLoading(false);
      return;
    }

    // Simulate login
    setTimeout(() => {
      localStorage.setItem('user', JSON.stringify({ 
        username, 
        role: 'super_admin',
        login_time: new Date().toISOString()
      }));
      window.location.href = '/';
    }, 500);
  };

  return (
    <div className="min-h-screen bg-dark-bg flex items-center justify-center p-4">
      <div className="glass-card w-full max-w-md p-8">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-2 mb-4">
            <div className="p-3 rounded-xl bg-primary-500/20 border border-primary-500/30">
              <Bot className="w-8 h-8 text-primary-400" />
            </div>
          </div>
          <h1 className="text-2xl font-bold gradient-text">NEMESIS AI</h1>
          <p className="text-sm text-dark-muted mt-1">Strategic Intelligence Center</p>
          <p className="text-xs text-dark-muted/60 mt-2">v8.0</p>
        </div>

        {/* Error */}
        {error && (
          <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3 mb-4">
            <p className="text-sm text-red-400">{error}</p>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="text-xs text-dark-muted block mb-1">Username</label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-dark-muted" />
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Enter username"
                className="w-full bg-dark-bg/50 border border-dark-border rounded-lg pl-9 pr-3 py-2.5 text-sm text-white placeholder-dark-muted focus:outline-none focus:border-primary-500/50"
                required
                autoFocus
              />
            </div>
          </div>

          <div>
            <label className="text-xs text-dark-muted block mb-1">Password</label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-dark-muted" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter password"
                className="w-full bg-dark-bg/50 border border-dark-border rounded-lg pl-9 pr-3 py-2.5 text-sm text-white placeholder-dark-muted focus:outline-none focus:border-primary-500/50"
                required
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading || !username || !password}
            className="w-full py-2.5 bg-primary-500 hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg text-sm text-white font-medium transition-colors flex items-center justify-center gap-2"
          >
            {loading ? (
              <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" />
            ) : (
              <>
                <LogIn className="w-4 h-4" />
                Login
              </>
            )}
          </button>
        </form>

        <div className="mt-6 text-center text-xs text-dark-muted/60">
          <p>Default: admin / admin123</p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
