// frontend/e2e/homepage.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Homepage', () => {
  test('should display hero section', async ({ page }) => {
    await page.goto('http://localhost:3000/');
    

    await expect(page.locator('h2:has-text("КАК ЭТО РАБОТАЕТ")')).toBeVisible();
    

    await expect(page.locator('a:has-text("Войти / Регистрация")')).toBeVisible();
  });
});