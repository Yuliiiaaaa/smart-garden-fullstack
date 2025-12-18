// apiClient.ts (с debug логированием)
import { API_BASE_URL, getAuthToken } from './apiConfig';

class ApiErrorClass extends Error {
  status: number;
  data?: any;

  constructor(message: string, status: number, data?: any) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

// Универсальная функция для запросов
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getAuthToken();
  
  console.log(`API Request to: ${endpoint}`);
  console.log(`Token exists: ${!!token}`);
  if (token) {
    console.log(`Token (first 20 chars): ${token.substring(0, 20)}...`);
  }
  
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  console.log('Request headers:', headers);

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    console.log(`Response status: ${response.status} ${response.statusText}`);

    if (!response.ok) {
      let errorData;
      try {
        errorData = await response.json();
      } catch {
        errorData = { message: response.statusText };
      }

      console.error('API Error:', errorData);
      throw new ApiErrorClass(
        errorData.detail || errorData.message || 'API Error',
        response.status,
        errorData
      );
    }

    // Если ответ 204 (No Content)
    if (response.status === 204) {
      return {} as T;
    }

    const data = await response.json();
    console.log('API Response data:', data);
    return data;
  } catch (error) {
    console.error('Fetch error:', error);
    throw error;
  }
}

// Функция для загрузки файлов
async function uploadFile<T>(
  endpoint: string,
  formData: FormData
): Promise<T> {
  const token = getAuthToken();
  
  console.log(`Upload to: ${endpoint}`);
  console.log(`Token exists: ${!!token}`);
  
  const headers: Record<string, string> = {};

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  console.log('Upload headers:', headers);

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers,
      body: formData,
    });

    console.log(`Upload response status: ${response.status} ${response.statusText}`);

    if (!response.ok) {
      const errorData = await response.json();
      console.error('Upload error:', errorData);
      throw new ApiErrorClass(
        errorData.detail || 'Upload failed',
        response.status,
        errorData
      );
    }

    const data = await response.json();
    console.log('Upload response data:', data);
    return data;
  } catch (error) {
    console.error('Upload fetch error:', error);
    throw error;
  }
}

export const apiClient = {
  get: <T>(endpoint: string) => apiRequest<T>(endpoint, { method: 'GET' }),
  post: <T>(endpoint: string, data: any) =>
    apiRequest<T>(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  put: <T>(endpoint: string, data: any) =>
    apiRequest<T>(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  patch: <T>(endpoint: string, data: any) =>
    apiRequest<T>(endpoint, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),
  delete: <T>(endpoint: string) =>
    apiRequest<T>(endpoint, { method: 'DELETE' }),
  upload: <T>(endpoint: string, formData: FormData) =>
    uploadFile<T>(endpoint, formData),
};