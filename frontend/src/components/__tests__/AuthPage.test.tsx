import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { HelmetProvider } from 'react-helmet-async';
import { AuthPage } from '../AuthPage';
import { authService } from '../../services/authService';

vi.mock('../../services/authService', () => ({
  authService: {
    login: vi.fn(),
    register: vi.fn(),
  },
}));

describe('AuthPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should login successfully', async () => {
    const mockLogin = authService.login as any;
    mockLogin.mockResolvedValue({ access_token: 'token', refresh_token: 'refresh', user: {} });

    render(
      <HelmetProvider>
        <BrowserRouter>
          <AuthPage />
        </BrowserRouter>
      </HelmetProvider>
    );

    fireEvent.change(screen.getByPlaceholderText(/example@mail.com/i), { target: { value: 'test@example.com' } });
    fireEvent.change(screen.getByPlaceholderText(/••••••••/i), { target: { value: 'password' } });
    fireEvent.click(screen.getByRole('button', { name: /войти/i }));

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith('test@example.com', 'password');
    });
  });

  it('should show error on failed login', async () => {
    const mockLogin = authService.login as any;
    mockLogin.mockRejectedValue(new Error('Invalid credentials'));

    render(
      <HelmetProvider>
        <BrowserRouter>
          <AuthPage />
        </BrowserRouter>
      </HelmetProvider>
    );

    fireEvent.change(screen.getByPlaceholderText(/example@mail.com/i), { target: { value: 'test@example.com' } });
    fireEvent.change(screen.getByPlaceholderText(/••••••••/i), { target: { value: 'wrong' } });
    fireEvent.click(screen.getByRole('button', { name: /войти/i }));

    await waitFor(() => {
      expect(screen.getByText(/Invalid credentials/i)).toBeInTheDocument();
    });
  });
});