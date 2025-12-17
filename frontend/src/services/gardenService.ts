// src/services/gardenService.ts
import { apiClient } from './apiClient';
import { Garden as GardenType, Tree as TreeType } from './apiConfig';

// Переименовываем интерфейсы, чтобы избежать конфликта
export interface GardenStats {
  garden_id: number;
  garden_name: string;
  total_trees: number;
  area_hectares: number;
  tree_density: number;
  harvest_records_count: number;
  average_fruits_per_tree: number;
  created_at: string | null;
  fruit_type: string;
}

// Используем другое имя для локального интерфейса дерева
export interface TreeData {
  id: number;
  garden_id: number;
  tree_number: number;
  row_number: number;
  fruit_type: string;
  created_at?: string;
  updated_at?: string;
}

export const gardenService = {
  // Получить все сады
  getAllGardens: async (skip = 0, limit = 100): Promise<GardenType[]> => {
    const response = await apiClient.get<GardenType[]>(
      `/gardens/?skip=${skip}&limit=${limit}`
    );
    return response;
  },

  // Получить сад по ID
  getGardenById: async (gardenId: number): Promise<GardenType> => {
    const response = await apiClient.get<GardenType>(`/gardens/${gardenId}`);
    return response;
  },

  // Получить статистику сада
  getGardenStats: async (gardenId: number): Promise<GardenStats> => {
    const response = await apiClient.get<GardenStats>(`/gardens/${gardenId}/stats`);
    return response;
  },

  // Создать сад
  createGarden: async (gardenData: {
    name: string;
    fruit_type: string;
    area: number;
  }): Promise<GardenType> => {
    const response = await apiClient.post<GardenType>('/gardens/', gardenData);
    return response;
  },

  // Получить деревья сада
  getGardenTrees: async (gardenId: number): Promise<TreeData[]> => {
    const response = await apiClient.get<TreeData[]>(`/trees/?garden_id=${gardenId}`);
    return response;
  },

  // Обновить информацию о саде
  updateGarden: async (gardenId: number, gardenData: {
    name?: string;
    fruit_type?: string;
    area?: number;
  }): Promise<GardenType> => {
    const response = await apiClient.put<GardenType>(`/gardens/${gardenId}`, gardenData);
    return response;
  },

  // Удалить сад
  deleteGarden: async (gardenId: number): Promise<{ message: string; deleted_id: number }> => {
    const response = await apiClient.delete<{ message: string; deleted_id: number }>(`/gardens/${gardenId}`);
    return response;
  },
};