/**
 * Authentication Context
 * Provides auth state and functions to the entire app
 */
import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import authService, { User, LoginResponse } from '../services/auth';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshToken: () => Promise<void>;
  updateUser: (data: Partial<User>) => Promise<void>;
  changePassword: (currentPassword: string, newPassword: string) => Promise<void>;
  hasRole: (role: string) => boolean;
  hasAnyRole: (roles: string[]) => boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Load user on mount
  useEffect(() => {
    const loadUser = async () => {
      try {
        const storedUser = authService.getUser();
        if (storedUser && authService.isAuthenticated()) {
          setUser(storedUser);
        } else if (authService.isAuthenticated()) {
          // Refresh user data
          const freshUser = await authService.getCurrentUser();
          setUser(freshUser);
          authService.setUser(freshUser);
        } else {
          authService.clearTokens();
          authService.clearUser();
        }
      } catch (error) {
        console.error('Failed to load user:', error);
        authService.clearTokens();
        authService.clearUser();
      } finally {
        setIsLoading(false);
      }
    };

    loadUser();
  }, []);

  const login = useCallback(async (username: string, password: string) => {
    setIsLoading(true);
    try {
      const response = await authService.login(username, password);
      authService.setTokens(response.access_token, response.refresh_token);
      authService.setUser(response.user);
      setUser(response.user);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const logout = useCallback(async () => {
    setIsLoading(true);
    try {
      await authService.logout();
    } finally {
      setUser(null);
      setIsLoading(false);
    }
  }, []);

  const refreshToken = useCallback(async () => {
    try {
      const response = await authService.refreshToken();
      const currentRefresh = authService.getRefreshToken();
      authService.setTokens(response.access_token, currentRefresh || '');
    } catch (error) {
      console.error('Failed to refresh token:', error);
      await logout();
    }
  }, [logout]);

  const updateUser = useCallback(async (data: Partial<User>) => {
    const updatedUser = await authService.updateProfile(data);
    setUser(updatedUser);
    authService.setUser(updatedUser);
  }, []);

  const changePassword = useCallback(async (currentPassword: string, newPassword: string) => {
    await authService.changePassword(currentPassword, newPassword);
  }, []);

  const hasRole = useCallback((role: string) => {
    return authService.hasRole(role);
  }, []);

  const hasAnyRole = useCallback((roles: string[]) => {
    return authService.hasAnyRole(roles);
  }, []);

  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated: !!user && authService.isAuthenticated(),
    login,
    logout,
    refreshToken,
    updateUser,
    changePassword,
    hasRole,
    hasAnyRole
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};