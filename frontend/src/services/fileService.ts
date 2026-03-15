import { apiClient } from './apiClient';

export const uploadFile = async (file: File): Promise<{ key: string }> => {
  const formData = new FormData();
  formData.append('file', file);
  return apiClient.upload<{ key: string }>('/files/upload', formData);
};

export const getPresignedUrl = async (key: string): Promise<{ url: string }> => {
  return apiClient.get<{ url: string }>(`/files/presigned/${encodeURIComponent(key)}`);
};