import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { GitLabCredentials } from '@/types/gitlab';

interface AuthContextType {
  credentials: GitLabCredentials | null;
  setCredentials: (credentials: GitLabCredentials | null) => void;
  isAuthenticated: boolean;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [credentials, setCredentials] = useState<GitLabCredentials | null>(() => {
    const stored = localStorage.getItem('gitlab_credentials');
    return stored ? JSON.parse(stored) : null;
  });

  useEffect(() => {
    if (credentials) {
      localStorage.setItem('gitlab_credentials', JSON.stringify(credentials));
    } else {
      localStorage.removeItem('gitlab_credentials');
    }
  }, [credentials]);

  const logout = () => {
    setCredentials(null);
    localStorage.removeItem('gitlab_credentials');
  };

  const value = {
    credentials,
    setCredentials,
    isAuthenticated: !!credentials?.access_token,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};