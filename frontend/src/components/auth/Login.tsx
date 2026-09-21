import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import authService from '../../services/auth';

export default function Login() {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      console.log('🔄 Attempting login...');
      
      // Get fresh instance of auth service
      const service = authService;
      
      // Login - this returns the LoginResponse
      const response = await service.login(username, password);
      console.log('✅ Login response received:', response);
      
      // Store tokens explicitly
      if (response.access_token) {
        service.setTokens(response.access_token, response.refresh_token);
        console.log('✅ Tokens stored:', {
          access_token: response.access_token.substring(0, 30) + '...',
          refresh_token: response.refresh_token ? response.refresh_token.substring(0, 30) + '...' : 'none'
        });
      } else {
        console.error('❌ No access_token in response:', response);
        setError('No access token received');
        setLoading(false);
        return;
      }
      
      // Store user data
      if (response.user) {
        service.setUser(response.user);
        console.log('✅ User stored:', response.user.username);
      }
      
      // Verify token was stored
      const storedToken = localStorage.getItem('access_token');
      console.log('🔑 Stored token after login:', storedToken ? storedToken.substring(0, 30) + '...' : 'null');
      
      if (storedToken) {
        toast.success('Login successful!');
        navigate('/dashboard', { replace: true });
      } else {
        console.error('❌ Token not stored properly');
        setError('Login failed - token storage issue');
      }
      
    } catch (err: any) {
      console.error('❌ Login error:', err);
      setError(err.response?.data?.detail || 'Invalid username or password');
      toast.error(err.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center">
      <div className="bg-gray-800 p-8 rounded-lg shadow-lg w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-white">NEMESIS V8+</h1>
          <p className="text-gray-400 mt-2">Intelligence Dashboard</p>
        </div>

        {error && (
          <div className="bg-red-500/20 border border-red-500 text-red-200 px-4 py-2 rounded-lg mb-4 text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-gray-300 text-sm font-medium mb-2">
              Username
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
              placeholder="Enter username"
              required
            />
          </div>

          <div className="mb-6">
            <label className="block text-gray-300 text-sm font-medium mb-2">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
              placeholder="Enter password"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <div className="mt-4 text-center text-sm text-gray-400">
          Enter your credentials
        </div>
      </div>
    </div>
  );
}
