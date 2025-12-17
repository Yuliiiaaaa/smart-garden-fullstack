// src/services/analysisService.ts
import { apiClient } from './apiClient';
import { AnalysisResult, AnalysisRequest } from './apiConfig';

export const analysisService = {
  // Анализ фотографии
  analyzePhoto: async (data: AnalysisRequest): Promise<AnalysisResult> => {
    const formData = new FormData();
    formData.append('file', data.file);
    formData.append('fruit_type', data.fruit_type);
    
    if (data.tree_id) {
      formData.append('tree_id', data.tree_id.toString());
    }

    const response = await apiClient.upload<AnalysisResult>(
      '/analysis/photo',
      formData
    );
    return response;
  },

  // Получить историю анализов
  getAnalysisHistory: async (
    treeId?: number,
    gardenId?: number,
    limit = 10
  ): Promise<any> => {
    const params = new URLSearchParams();
    if (treeId) params.append('tree_id', treeId.toString());
    if (gardenId) params.append('garden_id', gardenId.toString());
    params.append('limit', limit.toString());

    const response = await apiClient.get<any>(
      `/analysis/history?${params.toString()}`
    );
    return response;
  },

  // Демо анализ
  demoAnalysis: async (): Promise<any> => {
    const response = await apiClient.get('/analysis/demo');
    return response;
  },

  // Калибровка детектора
  calibrateDetector: async (
    file: File,
    expectedCount: number,
    fruitType: string = 'apple'
  ): Promise<any> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('expected_count', expectedCount.toString());
    formData.append('fruit_type', fruitType);

    const response = await apiClient.upload('/analysis/calibrate', formData);
    return response;
  },
};