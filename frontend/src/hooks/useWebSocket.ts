import { useEffect, useState, useCallback } from 'react';

interface WebSocketState {
  connected: boolean;
  messages: any[];
  error: string | null;
}

export function useWebSocket(url?: string) {
  const [state, setState] = useState<WebSocketState>({
    connected: false,
    messages: [],
    error: null,
  });

  const connect = useCallback(() => {
    setState(prev => ({ ...prev, connected: true }));
  }, []);

  const disconnect = useCallback(() => {
    setState(prev => ({ ...prev, connected: false }));
  }, []);

  const sendMessage = useCallback((data: any) => {
    if (state.connected) {
      console.log('WebSocket send:', data);
      setState(prev => ({
        ...prev,
        messages: [...prev.messages, { type: 'sent', data, timestamp: new Date().toISOString() }],
      }));
    }
  }, [state.connected]);

  useEffect(() => {
    connect();
    return () => disconnect();
  }, [connect, disconnect]);

  return {
    connected: state.connected,
    messages: state.messages,
    error: state.error,
    sendMessage,
    connect,
    disconnect,
  };
}

export default useWebSocket;
