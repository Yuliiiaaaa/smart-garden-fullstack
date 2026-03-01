// src/services/userService.ts
import { apiClient } from './apiClient';
import { User } from './apiConfig';

export const userService = {
  // Получить всех пользователей (admin only)
  getAllUsers: async (skip = 0, limit = 100): Promise<User[]> => {
    return apiClient.get<User[]>(`/auth/users?skip=${skip}&limit=${limit}`);
  },

  // Получить информацию о пользователе по ID (admin only)
  getUserById: async (userId: number): Promise<User> => {
    return apiClient.get<User>(`/auth/users/${userId}`);
  },

  // Изменить роль пользователя (admin only)
  changeUserRole: async (userId: number, role: string): Promise<User> => {
    return apiClient.put<User>(`/auth/users/${userId}/role`, { role });
  },
};