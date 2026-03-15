// src/services/apiClient.ts
import { API_BASE_URL, getAuthToken, getRefreshToken, setAuthToken, setRefreshToken, removeTokens } from './apiConfig';
import { authService } from './authService';

export class ApiError extends Error {
  status: number;
  data?: any;
  constructor(message: string, status: number, data?: any) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

let isRefreshing = false;
let failedQueue: { resolve: (value: any) => void; reject: (reason?: any) => void; }[] = [];

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {},
  retry = true
): Promise<T> {
  let token = getAuthToken();

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  try {
    let response = await fetch(`${API_BASE_URL}${endpoint}`, { ...options, headers });

    // Если 401 и есть refresh token, пробуем обновить
    if (response.status === 401 && retry) {
      const refreshToken = getRefreshToken();
      if (!refreshToken) {
        removeTokens();
        throw new ApiError('Требуется авторизация', 401);
      }

      if (!isRefreshing) {
        isRefreshing = true;
        try {
          const newAuth = await authService.refreshToken(refreshToken);
          setAuthToken(newAuth.access_token);
          setRefreshToken(newAuth.refresh_token);
          processQueue(null, newAuth.access_token);
          
          // Повторяем исходный запрос
          headers['Authorization'] = `Bearer ${newAuth.access_token}`;
          response = await fetch(`${API_BASE_URL}${endpoint}`, { ...options, headers });
        } catch (refreshError) {
          processQueue(refreshError, null);
          removeTokens();
          throw new ApiError('Сессия истекла. Войдите снова.', 401);
        } finally {
          isRefreshing = false;
        }
      } else {
        // Ставим в очередь
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then((newToken: any) => {
          headers['Authorization'] = `Bearer ${newToken}`;
          return fetch(`${API_BASE_URL}${endpoint}`, { ...options, headers });
        }).then(res => res.json());
      }
    }

    if (!response.ok) {
      let errorData;
      try {
        errorData = await response.json();
      } catch {
        errorData = { message: response.statusText };
      }
      throw new ApiError(
        errorData.detail || errorData.message || 'API Error',
        response.status,
        errorData
      );
    }

    if (response.status === 204) {
      return {} as T;
    }

    return await response.json() as T;
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new ApiError((error as Error).message, 500);
  }
}

async function uploadFile<T>(
  endpoint: string,
  formData: FormData
): Promise<T> {
  const token = getAuthToken();
  
  const headers: Record<string, string> = {};

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers,
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new ApiError(
        errorData.detail || 'Upload failed',
        response.status,
        errorData
      );
    }

    return await response.json() as T;
  } catch (error) {
    console.error('Upload fetch error:', error);
    throw error;
  }
}

export const apiClient = {
  get: <T>(endpoint: string): Promise<T> => 
    apiRequest<T>(endpoint, { method: 'GET' }),
    
  post: <T>(endpoint: string, data: any): Promise<T> =>
    apiRequest<T>(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    }),
    
  put: <T>(endpoint: string, data: any): Promise<T> =>
    apiRequest<T>(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
    
  patch: <T>(endpoint: string, data: any): Promise<T> =>
    apiRequest<T>(endpoint, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),
    
  delete: <T>(endpoint: string): Promise<T> =>
    apiRequest<T>(endpoint, { method: 'DELETE' }),
    
  upload: <T>(endpoint: string, formData: FormData): Promise<T> =>
    uploadFile<T>(endpoint, formData),
};