import { test, expect } from '@playwright/test';
import { login } from './helpers';

test.describe('Weather widget', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin@example.com', 'admin123');
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');
  });

  test('should display weather for each garden or fallback', async ({ page }) => {
    const weatherWidget = page.locator('.bg-blue-50, .text-amber-600').first();
    await expect(weatherWidget).toBeVisible();
    const text = await weatherWidget.textContent();
    expect(text).toMatch(/°C|Погода временно недоступна/i);
  });

  test('should handle API failure gracefully', async ({ page }) => {
    await page.route('**/api/v1/weather/*', route => route.abort());
    await page.reload();
    await page.waitForLoadState('networkidle');
    // Ищем либо сообщение об ошибке, либо виджет с ошибкой
    const errorIndicator = page.locator('.text-amber-600').first();
    await expect(errorIndicator).toBeVisible();
    // Можно проверить, что текст содержит не °C (т.е. ошибка)
    const text = await errorIndicator.textContent();
    expect(text).not.toContain('°C');
  });
});