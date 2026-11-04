import { test, expect } from '@playwright/test';

test('home page lists every coin', async ({ page }) => {
  await page.goto('/');
  await expect(page.locator('a[href^="recharge.html?app="]')).toHaveCount(13);
});

test('admin orders table fits a phone screen', async ({ page }) => {
  await page.goto('/admin/login/');
  await page.fill('#id_username', 'admin');
  await page.fill('#id_password', 'Admin@CoinHub2025!');
  await page.keyboard.press('Enter');
  await page.goto('/admin/orders/order/');
  await expect(page.locator('#result_list')).toBeVisible();
  const overflow = await page.evaluate(
    () => document.documentElement.scrollWidth > window.innerWidth
  );
  expect(overflow).toBe(false);   // no sideways page scroll
});