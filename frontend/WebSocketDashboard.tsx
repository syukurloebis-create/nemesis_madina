// WebSocketDashboard.tsx
import React, { useEffect } from 'react';
import useWebSocket from './src/hooks/useWebSocket';
import { useAuthStore } from './src/stores/authStore';

export default function WebSocketDashboard() {
  const { token, getToken, user, login, logout } = useAuthStore();
  const [isLoggedIn, setIsLoggedIn] = React.useState(!!token);

  const {
    connected,
    authError,
    lastMessage,
    send,
  } = useWebSocket(`ws://localhost:8000/ws/${user?.id || 'dashboard'}`, {
    autoConnect: isLoggedIn && !!token,
    getToken: getToken,  // ← KIRIM FUNGSI GET TOKEN
    reconnectInterval: 3000,
    maxReconnectAttempts: 5,
  });

  useEffect(() => {
    if (lastMessage) {
      console.log('📨 Received:', lastMessage);
    }
  }, [lastMessage]);

  const handleLogin = async () => {
    try {
      await login('admin', 'admin123');
      setIsLoggedIn(true);
    } catch (err) {
      console.error('Login failed:', err);
    }
  };

  const handleLogout = () => {
    logout();
    setIsLoggedIn(false);
  };

  const sendTestMessage = () => {
    send({ type: 'ping', message: 'Hello from dashboard!' });
  };

  if (!isLoggedIn) {
    return (
      <div className="p-8 text-center">
        <h1 className="text-2xl font-bold mb-4">WebSocket Dashboard</h1>
        <button
          onClick={handleLogin}
          className="bg-blue-500 text-white px-4 py-2 rounded"
        >
          Login to Connect WebSocket
        </button>
      </div>
    );
  }

  return (
    <div className="p-4">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">WebSocket Dashboard</h1>
        <button
          onClick={handleLogout}
          className="bg-red-500 text-white px-4 py-2 rounded"
        >
          Logout
        </button>
      </div>

      <div className="grid gap-4 mb-4">
        <div className={`p-4 rounded ${connected ? 'bg-green-100' : authError ? 'bg-red-100' : 'bg-yellow-100'}`}>
          <div className="font-bold">Status:</div>
          <div>
            {connected ? '✅ Connected & Authenticated' : 
             authError ? '❌ Authentication Failed' : '🔌 Disconnected'}
          </div>
        </div>

        {connected && (
          <button
            onClick={sendTestMessage}
            className="bg-purple-500 text-white px-4 py-2 rounded w-48"
          >
            Send Test Message
          </button>
        )}
      </div>

      <div className="border rounded p-4">
        <h2 className="font-bold mb-2">Last Message:</h2>
        <pre className="bg-gray-100 p-2 rounded overflow-auto">
          {lastMessage ? JSON.stringify(lastMessage, null, 2) : 'No messages yet'}
        </pre>
      </div>
    </div>
  );
}