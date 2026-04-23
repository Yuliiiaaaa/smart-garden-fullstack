// frontend/src/services/__tests__/authService.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { authService } from '../authService';
import { apiClient } from '../apiClient';

vi.mock('../apiClient', () => ({
  apiClient: {
    post: vi.fn().mockResolvedValue({
      access_token: 'mock',
      refresh_token: 'mock',
      token_type: 'bearer',
      user: {}
    }),
    get: vi.fn(),
  },
}));

describe('authService', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.clearAllMocks();
  });

  it('should login and store tokens', async () => {
    const mockResponse = {
      access_token: 'access123',
      refresh_token: 'refresh123',
      token_type: 'bearer',
      user: { id: 1, email: 'test@example.com', full_name: 'Test User', role: 'user' }
    };
    (apiClient.post as any).mockResolvedValue(mockResponse);

    const result = await authService.login('test@example.com', 'password123');
    
    expect(result).toEqual(mockResponse);
    expect(localStorage.getItem('access_token')).toBe('access123');
    expect(localStorage.getItem('refresh_token')).toBe('refresh123');
  });
});