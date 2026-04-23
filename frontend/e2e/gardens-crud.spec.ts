import { test, expect } from '@playwright/test';
import { login } from './helpers';

test.describe('Gardens CRUD', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'manager@example.com', 'manager123');
    await page.goto('/gardens/manage');
    // Ждём загрузки страницы (например, заголовка)
    await expect(page.locator('h1')).toContainText('Управление садами', { timeout: 15000 });
    // Ждём появления формы (можно по кнопке "Создать сад" или полю ввода)
    await expect(page.locator('button:has-text("Создать сад")')).toBeVisible();
  });

  test('should create new garden', async ({ page }) => {
    const gardenName = `Тестовый сад ${Date.now()}`;
    await page.fill('input[placeholder="Название сада"]', gardenName);
    await page.fill('input[placeholder="Местоположение"]', 'Тестовая локация');
    await page.selectOption('select', 'apple');
    await page.fill('input[type="number"]', '2.5');
    await page.click('button:has-text("Создать сад")');
    await expect(page.locator(`text=${gardenName}`)).toBeVisible({ timeout: 10000 });
  });

  test('should delete garden', async ({ page }) => {
    const gardenCard = page.locator('.border.rounded').first();
    await expect(gardenCard).toBeVisible();
    const gardenName = await gardenCard.locator('.font-semibold').textContent();
    await gardenCard.locator('button:has-text("Удалить")').click();
    page.on('dialog', dialog => dialog.accept());
    await expect(page.locator(`text=${gardenName}`)).not.toBeVisible({ timeout: 10000 });
  });
});