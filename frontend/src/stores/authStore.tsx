import { create } from 'zustand';
import apiClient from '../services/api/client';

interface AuthState {
  user: any | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  isAuthenticated: false,
  login: async (username: string, password: string) => {
    const response = await apiClient.post('/auth/login', { username, password });
    set({ user: response.data.user, token: response.data.access_token, isAuthenticated: true });
  },
  logout: () => {
    set({ user: null, token: null, isAuthenticated: false });
  },
}));
