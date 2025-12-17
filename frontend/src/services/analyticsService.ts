// src/services/analyticsService.ts
import { apiClient } from './apiClient';

export const analyticsService = {
  // Получить общую аналитику
  getOverview: async (gardenId?: number, period = 'month'): Promise<any> => {
    const params = new URLSearchParams();
    if (gardenId) params.append('garden_id', gardenId.toString());
    params.append('period', period);

    const response = await apiClient.get(
      `/analytics/overview?${params.toString()}`
    );
    return response;
  },

  // Получить динамику роста
  getGrowth: async (gardenId?: number): Promise<any> => {
    const params = new URLSearchParams();
    if (gardenId) params.append('garden_id', gardenId.toString());

    const response = await apiClient.get(
      `/analytics/growth?${params.toString()}`
    );
    return response;
  },

  // Получить прогнозы
  getPredictions: async (gardenId?: number): Promise<any> => {
    const params = new URLSearchParams();
    if (gardenId) params.append('garden_id', gardenId.toString());

    const response = await apiClient.get(
      `/analytics/predictions?${params.toString()}`
    );
    return response;
  },
};