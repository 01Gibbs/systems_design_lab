import { test, expect } from '@playwright/test';
const BACKEND_URL = 'http://localhost:8000';
const FRONTEND_URL = 'http://localhost:5173';

test.describe('Simulator Control Panel - Error Handling', () => {
  test('shows error banner if backend is down', async ({ page }) => {
    // Simulate backend down by using a wrong URL
    await page.goto(FRONTEND_URL, { waitUntil: 'domcontentloaded' });
    // Simulate fetch failure by blocking network (Playwright API)
    await page.route('**/api/sim/*', route => route.abort());
    // Try to trigger a fetch (reload or action)
    await page.reload();
    // Should show error banner or message
    await expect(page.getByText(/failed to load/i)).toBeVisible();
  });
});
