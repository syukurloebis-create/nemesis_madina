import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import useWebSocket from '../hooks/useWebSocket';

const API_URL = 'http://localhost';

interface DashboardStats {
  total_cases: number;
  cases_by_status: Record<string, number>;
  cases_by_priority: Record<string, number>;
  api_instances: number;
  status: string;
}

export default function Dashboard() {
  const navigate = useNavigate();
  const { user, logout, token } = useAuthStore();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [wsMessages, setWsMessages] = useState<any[]>([]);

  const { connected, authError, lastMessage, send } = useWebSocket(
    `/ws/${user?.id || 'dashboard'}`,
    {
      autoConnect: !!token,
      onMessage: (msg) => {
        setWsMessages((prev) => [msg, ...prev].slice(0, 50));
      },
      onConnect: () => {
        console.log('🎉 WebSocket connected to dashboard');
        send({ type: 'echo', data: 'Hello from dashboard!' });
      },
      onAuthError: () => {
        console.error('WebSocket auth failed, token might be expired');
      },
    }
  );

  useEffect(() => {
    const fetchStats = async () => {
      try {
        console.log(`📊 Fetching stats from: ${API_URL}/api/dashboard/summary`);
        const response = await fetch(`${API_URL}/api/dashboard/summary`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
        if (response.ok) {
          const data = await response.json();
          setStats(data);
          console.log('✅ Stats fetched:', data);
        } else {
          console.error('Failed to fetch stats:', response.status);
        }
      } catch (err) {
        console.error('Failed to fetch stats:', err);
      }
    };

    if (token) {
      fetchStats();
    }
  }, [token]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleSendTestMessage = () => {
    send({ 
      type: 'echo', 
      data: `Test message at ${new Date().toLocaleTimeString()}` 
    });
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-800">Nemesis Madina V8</h1>
          <div className="flex items-center gap-4">
            <div className="text-right">
              <div className="text-sm font-medium text-gray-700">{user?.full_name}</div>
              <div className="text-xs text-gray-500">{user?.role} • {user?.institution_id}</div>
            </div>
            <button
              onClick={handleLogout}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-6 p-4 bg-white rounded-lg shadow">
          <div className="flex items-center justify-between">
            <div>
              <span className="font-medium">WebSocket Status:</span>
              {connected ? (
                <span className="ml-2 text-green-600">✅ Connected & Authenticated</span>
              ) : authError ? (
                <span className="ml-2 text-red-600">❌ Auth Error</span>
              ) : (
                <span className="ml-2 text-yellow-600">🔄 Connecting...</span>
              )}
            </div>
            <button
              onClick={handleSendTestMessage}
              disabled={!connected}
              className="px-3 py-1 bg-purple-600 text-white rounded hover:bg-purple-700 disabled:opacity-50"
            >
              Send Test Message
            </button>
          </div>
        </div>

        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white p-6 rounded-lg shadow">
              <div className="text-3xl font-bold text-blue-600">{stats.total_cases}</div>
              <div className="text-gray-600">Total Cases</div>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <div className="text-3xl font-bold text-green-600">
                {stats.cases_by_status?.open || 0}
              </div>
              <div className="text-gray-600">Open Cases</div>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <div className="text-3xl font-bold text-red-600">
                {stats.cases_by_priority?.critical || 0}
              </div>
              <div className="text-gray-600">Critical Priority</div>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <div className="text-3xl font-bold text-gray-600">
                {stats.api_instances || 1}
              </div>
              <div className="text-gray-600">API Instances</div>
            </div>
          </div>
        )}

        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-semibold mb-4">Real-time Messages</h2>
          {wsMessages.length === 0 ? (
            <p className="text-gray-500">No messages yet...</p>
          ) : (
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {wsMessages.map((msg, idx) => (
                <div key={idx} className="p-2 bg-gray-50 rounded text-sm font-mono">
                  <pre className="whitespace-pre-wrap">
                    {JSON.stringify(msg, null, 2)}
                  </pre>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
