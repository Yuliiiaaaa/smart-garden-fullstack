// src/services/authService.ts
import { apiClient } from './apiClient';
import { AuthResponse, User } from './apiConfig';

export const authService = {
  login: async (email: string, password: string): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>('/auth/login', {
      email,
      password,
    });
    return response;
  },

  register: async (
    email: string,
    password: string,
    full_name: string,
    role?: string
  ): Promise<User> => {
    const response = await apiClient.post<User>('/auth/register', {
      email,
      password,
      full_name,
      role: role || 'user',
    });
    return response;
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get<User>('/auth/me');
    return response;
  },
};
