// src/services/authService.ts
import { apiClient } from './apiClient';
import { AuthResponse, User, setAuthToken, setRefreshToken, removeTokens } from './apiConfig';

export const authService = {
  login: async (email: string, password: string): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>('/auth/login', { email, password });
    setAuthToken(response.access_token);
    setRefreshToken(response.refresh_token);
    localStorage.setItem('user', JSON.stringify(response.user));
    return response;
  },

  register: async (email: string, password: string, full_name: string): Promise<User> => {
    return apiClient.post<User>('/auth/register', { email, password, full_name });
  },

  refreshToken: async (refreshToken: string): Promise<AuthResponse> => {
    return apiClient.post<AuthResponse>('/auth/refresh', { refresh_token: refreshToken });
  },

  logout: async (refreshToken: string): Promise<void> => {
    try {
      await apiClient.post('/auth/logout', { refresh_token: refreshToken });
    } finally {
      removeTokens();
    }
  },

  logoutAll: async (): Promise<void> => {
    try {
      await apiClient.post('/auth/logout-all', {});
    } finally {
      removeTokens();
    }
  },

  getCurrentUser: async (): Promise<User> => {
    return apiClient.get<User>('/auth/me');
  },
};