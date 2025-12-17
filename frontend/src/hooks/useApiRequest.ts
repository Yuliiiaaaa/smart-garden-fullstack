// src/hooks/useApiRequest.ts
import { useState, useCallback } from 'react';
import { ApiError } from '../services/apiConfig';

export function useApiRequest<T>() {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const execute = useCallback(
    async (requestFn: () => Promise<T>) => {
      setLoading(true);
      setError(null);
      
      try {
        const result = await requestFn();
        setData(result);
        return result;
      } catch (err: any) {
        const apiError = err as ApiError;
        setError(apiError.message || 'Произошла ошибка');
        throw err;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setLoading(false);
  }, []);

  return {
    data,
    loading,
    error,
    execute,
    reset,
  };
}