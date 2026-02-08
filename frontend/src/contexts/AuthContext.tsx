import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { apiClient, UserResponse } from '../services/api';

interface AuthContextType {
  user: UserResponse | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (phone: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<UserResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const isAuthenticated = !!user && apiClient.isAuthenticated();

  // Проверяем авторизацию при загрузке приложения
  useEffect(() => {
    const checkAuth = async () => {
      if (apiClient.isAuthenticated()) {
        try {
          const userData = await apiClient.getCurrentUser();
          setUser(userData);
        } catch (error) {
          console.error('Failed to get current user:', error);
          apiClient.logout();
        }
      }
      setIsLoading(false);
    };

    checkAuth();
  }, []);

  const login = async (phone: string, password: string) => {
    try {
      setIsLoading(true);
      await apiClient.login({ phone, password });
      const userData = await apiClient.getCurrentUser();
      setUser(userData);
    } catch (error: any) {
      console.error('Login failed:', error);
      // Улучшаем сообщение об ошибке
      if (error.response?.data?.detail) {
        const detail = error.response.data.detail;
        if (detail.includes('Exception') || detail.includes('Error')) {
          throw new Error('Ошибка входа в систему');
        } else {
          throw new Error(detail);
        }
      } else {
        throw new Error('Ошибка входа в систему');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      await apiClient.logoutUser();
    } catch (error) {
      console.error('Logout failed:', error);
    } finally {
      setUser(null);
      apiClient.logout();
    }
  };

  const refreshUser = async () => {
    if (apiClient.isAuthenticated()) {
      try {
        const userData = await apiClient.getCurrentUser();
        setUser(userData);
      } catch (error) {
        console.error('Failed to refresh user:', error);
        apiClient.logout();
      }
    }
  };

  const value: AuthContextType = {
    user,
    isAuthenticated,
    isLoading,
    login,
    logout,
    refreshUser,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
