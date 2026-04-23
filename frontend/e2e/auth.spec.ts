import { test, expect } from '@playwright/test';
import { login } from './helpers';

test.describe('Authentication E2E', () => {
  test('should login with valid credentials', async ({ page }) => {
    await page.goto('/auth');
    await page.fill('input[type="email"]', 'admin@example.com');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('h1')).toContainText('Добро пожаловать');
  });

  test('should show error on invalid credentials', async ({ page }) => {
    await page.goto('/auth');
    await page.fill('input[type="email"]', 'wrong@example.com');
    await page.fill('input[type="password"]', 'wrongpass');
    await page.click('button[type="submit"]');
    // Сообщение может быть "Неверный email или пароль" или "Требуется авторизация"
    const errorLocator = page.locator('.bg-red-100');
    await expect(errorLocator).toBeVisible();
    const errorText = await errorLocator.textContent();
    expect(errorText).toMatch(/Неверный email|Требуется авторизация/i);
  });

  test('should logout successfully', async ({ page }) => {
    await login(page, 'admin@example.com', 'admin123');
    await page.click('button[aria-label="Выйти"]');
    await expect(page).toHaveURL('/');
    await expect(page.locator('text=Войти / Регистрация')).toBeVisible();
  });
});