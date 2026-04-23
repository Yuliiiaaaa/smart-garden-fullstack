import { test, expect } from '@playwright/test';
import { login } from './helpers';

test.describe('Gardens filters and pagination', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'admin@example.com', 'admin123');
    await page.goto('/gardens');
    await expect(page.locator('input[placeholder="Название сада"]')).toBeVisible({ timeout: 10000 });
  });

  test('should filter by name', async ({ page }) => {
    await page.fill('input[placeholder="Название сада"]', 'Яблоневый');
    await page.click('button:has-text("Применить")');
    await page.waitForTimeout(1000);
    const gardens = page.locator('.bg-white.p-4.rounded');
    await expect(gardens).toHaveCount(1);
    await expect(gardens.first()).toContainText('Яблоневый');
  });

  test('should sort by area descending', async ({ page }) => {
    // Ждём, пока select станет активным
    await expect(page.locator('select').first()).toBeEnabled();
    await page.selectOption('select', 'area');
    await expect(page.locator('select:last-of-type')).toBeEnabled();
    await page.selectOption('select:last-of-type', 'desc');
    await page.click('button:has-text("Применить")');
    await page.waitForTimeout(1500);
    const areas = await page.locator('.bg-white.p-4 .font-medium').allTextContents();
    const numericAreas = areas.map(a => parseFloat(a.split(' ')[0]));
    for (let i = 0; i < numericAreas.length - 1; i++) {
      expect(numericAreas[i]).toBeGreaterThanOrEqual(numericAreas[i + 1]);
    }
  });

  test('should paginate correctly', async ({ page }) => {
    // Находим select с текущим значением "10" (поле limit)
    await page.locator('select').nth(3).selectOption('2');
    await page.click('button:has-text("Применить")');
    await page.waitForTimeout(1000);
    const firstPageCount = await page.locator('.bg-white.p-4').count();
    expect(firstPageCount).toBeLessThanOrEqual(2);
    await page.click('button:has-text("Вперёд")');
    const secondPageCount = await page.locator('.bg-white.p-4').count();
    expect(secondPageCount).toBeGreaterThan(0);
  });
});