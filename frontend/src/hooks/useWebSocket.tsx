import { useEffect, useRef, useState, useCallback } from 'react';

const WS_BASE_URL = import.meta.env.VITE_WS_URL || 'ws://localhost';

export default function useWebSocket(clientId?: string) {
  const [connected, setConnected] = useState(false);
  const [authError, setAuthError] = useState(false);
  const [lastMessage, setLastMessage] = useState<any>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;

  // Helper to get token from localStorage
  const getToken = useCallback((): string | null => {
    // Try direct access_token first
    let token = localStorage.getItem('access_token');
    if (token) {
      return token;
    }
    
    // Try to parse from auth-storage
    try {
      const authStorage = localStorage.getItem('auth-storage');
      if (authStorage) {
        const parsed = JSON.parse(authStorage);
        token = parsed.state?.token;
        if (token) {
          // Sync to access_token for consistency
          localStorage.setItem('access_token', token);
          return token;
        }
      }
    } catch (e) {
      console.error('Failed to parse auth-storage:', e);
    }
    
    return null;
  }, []);

  const connect = useCallback(() => {
    const token = getToken();
    
    if (!token) {
      console.log('🔐 No token available, skipping WebSocket connection');
      return;
    }

    // Sanitize clientId
    let cleanClientId = clientId || 'dashboard';
    if (cleanClientId.includes('/ws/')) {
      cleanClientId = cleanClientId.split('/ws/').pop() || 'dashboard';
    }
    if (cleanClientId.startsWith('/')) {
      cleanClientId = cleanClientId.substring(1);
    }
    
    const wsUrl = `${WS_BASE_URL}/ws/${cleanClientId}`;
    console.log(`🔌 Connecting to WebSocket: ${wsUrl}`);
    console.log(`🔐 Token (first 30 chars): ${token.substring(0, 30)}...`);
    
    const ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
      console.log('🔌 WebSocket opened, sending auth...');
      ws.send(JSON.stringify({ type: 'auth', token }));
    };
    
    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        console.log('📨 WebSocket message:', message);
        
        if (message.type === 'auth_success') {
          setConnected(true);
          setAuthError(false);
          reconnectAttempts.current = 0;
          console.log('✅ WebSocket authenticated successfully');
        } else if (message.type === 'auth_error') {
          setAuthError(true);
          setConnected(false);
          console.error('❌ WebSocket auth error:', message.message);
          ws.close();
        } else {
          setLastMessage(message);
        }
      } catch (err) {
        console.error('Failed to parse message:', err);
      }
    };
    
    ws.onclose = (event) => {
      console.log(`🔌 WebSocket closed: ${event.code} - ${event.reason || 'No reason'}`);
      setConnected(false);
      
      // Don't reconnect on auth error (1008)
      if (event.code === 1008) {
        console.log('🔐 Auth error, will not auto-reconnect');
        setAuthError(true);
        return;
      }
      
      if (reconnectAttempts.current < maxReconnectAttempts) {
        reconnectAttempts.current++;
        const delay = Math.min(3000 * reconnectAttempts.current, 30000);
        console.log(`🔄 Reconnecting in ${delay}ms... (${reconnectAttempts.current}/${maxReconnectAttempts})`);
        
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
        }
        reconnectTimeoutRef.current = setTimeout(connect, delay);
      }
    };
    
    ws.onerror = (err) => {
      console.error('WebSocket error:', err);
    };
    
    wsRef.current = ws;
  }, [clientId, getToken]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setConnected(false);
    reconnectAttempts.current = 0;
  }, []);

  const send = useCallback((data: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
      return true;
    }
    console.warn('WebSocket not ready, message not sent');
    return false;
  }, []);

  useEffect(() => {
    connect();
    return () => disconnect();
  }, [connect, disconnect]);

  return { connected, authError, lastMessage, send, disconnect };
}
