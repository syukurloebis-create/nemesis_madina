import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { api } from '../services/api';

interface User {
  id: string;
  username: string;
  full_name: string;
  email: string;
  role: string;
  institution_id: string | null;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  error: string | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: () => boolean;
  getToken: () => string | null;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isLoading: false,
      error: null,

      login: async (username: string, password: string) => {
        set({ isLoading: true, error: null });
        try {
          const response = await api.login(username, password);
          // Store token in both store and localStorage
          const token = response.access_token;
          localStorage.setItem('access_token', token);
          set({
            user: response.user,
            token: token,
            isLoading: false,
            error: null,
          });
          console.log('✅ Login successful, token stored in both locations');
        } catch (error: any) {
          console.error('❌ Login failed:', error.message);
          set({
            isLoading: false,
            error: error.message || 'Login failed',
          });
          throw error;
        }
      },

      logout: () => {
        api.logout();
        localStorage.removeItem('access_token');
        set({ user: null, token: null, error: null });
        console.log('👋 Logged out, token removed');
      },

      isAuthenticated: () => {
        const hasToken = !!get().token || !!localStorage.getItem('access_token');
        return hasToken;
      },

      getToken: () => {
        // Try to get from store first, then localStorage
        const storeToken = get().token;
        if (storeToken) return storeToken;
        
        const storedToken = localStorage.getItem('access_token');
        if (storedToken) {
          // Sync back to store
          set({ token: storedToken });
          return storedToken;
        }
        return null;
      },
    }),
    {
      name: 'auth-storage',
      getStorage: () => localStorage,
    }
  )
);
