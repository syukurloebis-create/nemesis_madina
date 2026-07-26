// src/stores/websocketStore.ts
import { create } from 'zustand';

interface WebSocketState {
  connected: boolean;
  lastMessage: any;
  connect: () => void;
  disconnect: () => void;
  sendMessage: (message: any) => void;
}

export const useWebSocketStore = create<WebSocketState>((set, get) => ({
  connected: false,
  lastMessage: null,

  connect: () => {
    set({ connected: true });
    console.log('WebSocket connected (mock mode)');
  },

  disconnect: () => {
    set({ connected: false });
    console.log('WebSocket disconnected');
  },

  sendMessage: (message) => {
    console.log('Sending message:', message);
  },
}));
