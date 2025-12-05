import React, { createContext, useContext, useState, useEffect } from 'react';
import { AuthResponse } from '../../shared/api';
import { api_v, base_url } from '../lib/utils';

interface AuthContextType {
  user: AuthResponse | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  setDevMode: (enabled: boolean) => void;
  isDevMode: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Mock dev user
const DEV_USER: AuthResponse = {
  id: 'dev-user-001',
  email: 'dev@example.com',
  name: 'Dev User',
  access_token: 'dev-token-mock',
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<AuthResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isDevMode, setIsDevMode] = useState(false);

  // Check if user is already logged in or in dev mode
  useEffect(() => {
    const checkAuth = async () => {
      // Check for dev mode query parameter
      const params = new URLSearchParams(window.location.search);
      if (params.get('dev') === 'true') {
        setUser(DEV_USER);
        setIsDevMode(true);
      } else {
        const token = localStorage.getItem('authToken');
        const userData = localStorage.getItem('userData');

        if (token && userData) {
          try {
            setUser(JSON.parse(userData));
          } catch {
            localStorage.removeItem('authToken');
            localStorage.removeItem('userData');
          }
        }
      }

      setIsLoading(false);
    };

    checkAuth();
  }, []);

  const login = async (email: string, password: string) => {
    try {
      const response = await fetch(`${base_url}${api_v}auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({ username: email, password }).toString(),
      });

      if (!response.ok) {
        throw new Error('Login failed');
      }

      const data: AuthResponse = await response.json();
      setUser(data);
      localStorage.setItem('authToken', data.access_token);
      localStorage.setItem('userData', JSON.stringify(data));
    } catch (error) {
      throw error;
    }
  };

  const register = async (email: string, password: string, name: string) => {
    try {
      const response = await fetch(`${base_url}${api_v}auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, username: name}),
      });

      if (!response.ok) {
        throw new Error('Registration failed');
      }

      const data: AuthResponse = await response.json();
      setUser(data);
      localStorage.setItem('authToken', data.access_token);
      localStorage.setItem('userData', JSON.stringify(data));
    } catch (error) {
      throw error;
    }
  };

  const logout = () => {
    setUser(null);
    setIsDevMode(false);
    localStorage.removeItem('authToken');
    localStorage.removeItem('userData');
  };

  const handleSetDevMode = (enabled: boolean) => {
    if (enabled) {
      setUser(DEV_USER);
      setIsDevMode(true);
    } else {
      setUser(null);
      setIsDevMode(false);
      localStorage.removeItem('authToken');
      localStorage.removeItem('userData');
    }
  };

  return (
    <AuthContext.Provider value={{
      user,
      isLoading,
      login,
      register,
      logout,
      isAuthenticated: !!user,
      setDevMode: handleSetDevMode,
      isDevMode,
    }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
