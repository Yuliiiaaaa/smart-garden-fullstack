// // frontend/src/services/__tests__/apiClient.test.ts
// import { describe, it, expect, vi, beforeEach } from 'vitest';
// import { apiClient } from '../apiClient';
// import { getAuthToken, setAuthToken, getRefreshToken } from '../apiConfig';

// vi.mock('../apiConfig', () => ({
//   getAuthToken: vi.fn(),
//   setAuthToken: vi.fn(),
//   getRefreshToken: vi.fn(),
//   removeTokens: vi.fn(),
//   API_BASE_URL: 'http://localhost:8000/api/v1',
// }));

// describe('apiClient', () => {
//   beforeEach(() => {
//     vi.resetAllMocks();
//   });

//   it('should retry with new token after 401', async () => {
//     const mockFetch = vi.fn()
//       .mockResolvedValueOnce({ ok: false, status: 401, json: async () => ({ detail: 'expired' }) })
//       .mockResolvedValueOnce({ ok: true, json: async () => ({ data: 'ok' }) });
//     global.fetch = mockFetch;

//     (getAuthToken as any).mockReturnValue('old_token');
//     (getRefreshToken as any).mockReturnValue('refresh_token');
//     (global as any).fetch = mockFetch;

//     // дополнительно мокаем запрос на refresh
//     const refreshFetch = vi.fn().mockResolvedValue({
//       ok: true,
//       json: async () => ({ access_token: 'new_token', refresh_token: 'new_rt' })
//     });
//     global.fetch = vi.fn()
//       .mockImplementation((url) => {
//         if (url.includes('/auth/refresh')) return refreshFetch();
//         return mockFetch();
//       });

//     const result = await apiClient.get('/test');
//     expect(result).toEqual({ data: 'ok' });
//     expect(setAuthToken).toHaveBeenCalledWith('new_token');
//   });
// });