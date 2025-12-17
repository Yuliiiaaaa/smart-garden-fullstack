// src/services/apiConfig.ts
export const API_BASE_URL = 'http://localhost:8000/api/v1';

// Базовые интерфейсы
export interface ApiError {
  message: string;
  status: number;
  data?: any;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  created_at: string;
}

// Интерфейсы для садов и деревьев
export interface Garden {
  id: number;
  name: string;
  fruit_type: string;
  area: number;
  created_at?: string;
  updated_at?: string;
}

export interface Tree {
  id: number;
  garden_id: number;
  tree_number: number;
  row_number: number;
  fruit_type: string;
  created_at?: string;
  updated_at?: string;
}

export interface AnalysisRequest {
  file: File;
  tree_id?: number;
  fruit_type: string;
  garden_id?: number;
  scale?: string;
}

export interface AnalysisResult {
  fruit_count: number;
  confidence: number;
  processing_time: number;
  detected_fruits: Array<{
    fruit_type: string;
    count: number;
    confidence: number;
    boxes: Array<[number, number, number, number]>;
  }>;
  recommendations: string;
  record_id: number;
  method: string;
  model: string;
}

// Функция для получения токена
export const getAuthToken = (): string | null => {
  return localStorage.getItem('token');
};

// Функция для установки токена
export const setAuthToken = (token: string): void => {
  localStorage.setItem('token', token);
};

// Функция для удаления токена
export const removeAuthToken = (): void => {
  localStorage.removeItem('token');
};