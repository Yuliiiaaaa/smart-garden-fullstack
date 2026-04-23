import { Page } from '@playwright/test';

export async function login(page: Page, email: string, password: string) {
  await page.goto('/auth');
  await page.fill('input[type="email"]', email);
  await page.fill('input[type="password"]', password);
  await page.click('button[type="submit"]');
  await page.waitForURL('/dashboard', { timeout: 10000 });
}

export async function waitForElement(page: Page, selector: string, timeout = 10000) {
  await page.waitForSelector(selector, { state: 'visible', timeout });
}