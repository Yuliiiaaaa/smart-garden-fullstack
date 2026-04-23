// frontend/e2e/analysis.spec.ts
import { test, expect } from '@playwright/test';
import { login } from './helpers';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

test.describe('Photo analysis', () => {
  test.beforeEach(async ({ page }) => {
    await login(page, 'user@example.com', 'user123');
    await page.goto('/analysis');
    await page.waitForLoadState('networkidle');
  });

  test('should upload and analyze photo', async ({ page }) => {
    const filePath = path.join(__dirname, 'fixtures', 'apple-tree.jpg');
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles(filePath);
    await expect(page.locator('.max-h-64')).toBeVisible();
    await page.click('button:has-text("НАЧАТЬ АНАЛИЗ")');
    await expect(page).toHaveURL(/\/results/, { timeout: 30000 });
    await expect(page.locator('text=АНАЛИЗ ЗАВЕРШЕН')).toBeVisible();
  });
});