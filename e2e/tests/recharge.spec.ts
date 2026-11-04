import { test, expect } from '@playwright/test';

test.describe('Recharge form', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/recharge.html?app=baat');
    await expect(page.locator('#appName')).toHaveText('Baat');
    await page.fill('#appUserId', '1234567890');   // 10 digits
  });

  for (const phone of ['712345678', '0712345678', '0112345678']) {
    test(`accepts phone ${phone}`, async ({ page }) => {
      await page.fill('#phoneNumber', phone);
      await page.fill('#coinQty', '1000');
      await expect(page.locator('#btnNext')).toBeEnabled();
    });
  }

  test('invalid amount snaps up to the next pack', async ({ page }) => {
    await page.goto('/recharge.html?app=boloup');
    await page.fill('#coinQty', '11000');
    await page.locator('#coinQty').press('Tab');
    await expect(page.locator('#coinQty')).toHaveValue('15000');
    await expect(page.locator('#kesAmount')).toHaveText('231');
    await expect(page.locator('#coinHint')).toContainText('packs of 5,000');
  });

  test('quick-pick button fills the amount', async ({ page }) => {
    await page.goto('/recharge.html?app=boloup');
    await page.locator('.coin-chip').nth(1).click();   // 2 packs
    await expect(page.locator('#coinQty')).toHaveValue('10000');
    await expect(page.locator('#kesAmount')).toHaveText('154');
  });

  test('calculates KES for 5000 Baat coins', async ({ page }) => {
    await page.fill('#coinQty', '5000');
    await expect(page.locator('#kesAmount')).toHaveText('75');  // 15 per 1000
  });

  test('confirm screen shows the full phone number', async ({ page }) => {
    await page.fill('#phoneNumber', '0712345678');
    await page.fill('#coinQty', '1000');
    await page.click('#btnNext');
    await expect(page.locator('#confPhone')).toHaveText('+254712345678');
  });
});