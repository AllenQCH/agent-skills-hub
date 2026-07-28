import { test, expect } from '@playwright/test';

// Acceptance QA Agent template
// Replace BASE_URL and selectors with product-specific values.
// Keep every test title prefixed with its Case ID.

const BASE_URL = process.env.ACCEPTANCE_BASE_URL || 'http://localhost:3000';

test.describe('Acceptance QA', () => {
  test('TC-001 core happy path works', async ({ page }) => {
    await page.goto(BASE_URL);

    // Prefer user-visible locators over brittle CSS selectors.
    // Example:
    // await page.getByRole('link', { name: /sign in/i }).click();
    // await page.getByLabel(/email/i).fill('qa@example.com');
    // await page.getByRole('button', { name: /submit/i }).click();

    await expect(page).toHaveTitle(/.+/);
  });

  test('TC-002 invalid input is rejected', async ({ page }) => {
    await page.goto(BASE_URL);

    // Example:
    // await page.getByRole('button', { name: /submit/i }).click();
    // await expect(page.getByText(/required|invalid/i)).toBeVisible();

    await expect(page.locator('body')).toBeVisible();
  });
});
