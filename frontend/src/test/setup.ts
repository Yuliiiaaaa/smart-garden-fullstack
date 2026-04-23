// frontend/src/test/setup.ts
import { afterEach, vi } from 'vitest';
import { cleanup } from '@testing-library/react';
import '@testing-library/jest-dom/vitest';
import React from 'react';

// Мок для HelmetProvider и Helmet
vi.mock('react-helmet-async', () => ({
  HelmetProvider: ({ children }: { children: React.ReactNode }) => React.createElement(React.Fragment, null, children),
  Helmet: ({ children }: { children: React.ReactNode }) => React.createElement(React.Fragment, null, children),
}));

// Мок для localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => { store[key] = value; },
    removeItem: (key: string) => { delete store[key]; },
    clear: () => { store = {}; },
  };
})();
Object.defineProperty(window, 'localStorage', { value: localStorageMock });

// Мок для fetch (используем window.fetch)
window.fetch = vi.fn();

// Мок для URL.createObjectURL и revokeObjectURL
window.URL.createObjectURL = vi.fn(() => 'mock-url');
window.URL.revokeObjectURL = vi.fn();

// Мок для matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// Очистка после каждого теста
afterEach(() => {
  cleanup();
});