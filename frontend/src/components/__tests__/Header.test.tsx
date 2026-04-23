// frontend/src/components/__tests__/Header.test.tsx
import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { HelmetProvider } from 'react-helmet-async';
import { Header } from '../Header';

beforeEach(() => {
  localStorage.setItem('user', JSON.stringify({ full_name: 'Test User', role: 'user' }));
});

describe('Header', () => {
  it('renders logo and navigation for logged in user', () => {
    render(
      <HelmetProvider>
        <BrowserRouter>
          <Header isLoggedIn={true} />
        </BrowserRouter>
      </HelmetProvider>
    );
    
    expect(screen.getByText('Умный Сад')).toBeInTheDocument();
    expect(screen.getByText('Дашборд')).toBeInTheDocument();
    expect(screen.getByText('Анализ')).toBeInTheDocument();
  });
});