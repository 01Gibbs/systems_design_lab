import { test, expect } from '@playwright/test';

const BACKEND_URL = 'http://localhost:8000';
const FRONTEND_URL = 'http://localhost:5173';

test.describe('Simulator Control Panel', () => {
  test.beforeEach(async ({ request }) => {
    // Reset simulator state via API before each test
    await request.post(`${BACKEND_URL}/api/sim/reset`);
  });

  test('enabling scenario via API shows banner with active count', async ({ page, request }) => {
    await page.goto(FRONTEND_URL);

    // Banner should not be visible initially
    await expect(page.getByText(/active scenario/i)).not.toBeVisible();

    // Enable via API (not UI clicks)
    await request.post(`${BACKEND_URL}/api/sim/enable`, {
      data: {
        scenario: 'fixed_latency',
        parameters: { target_route: '/api/sim/scenarios', delay_ms: 100 },
      },
    });

    // Wait for banner to appear (polls every 2s)
    await expect(page.getByText(/1 active scenario/i)).toBeVisible({ timeout: 5000 });
  });

  test('page lists scenario name after enable', async ({ page, request }) => {
    // Enable via API
    await request.post(`${BACKEND_URL}/api/sim/enable`, {
      data: {
        scenario: 'fixed_latency',
        parameters: { target_route: '/api/sim/scenarios', delay_ms: 100 },
      },
    });

    await page.goto(FRONTEND_URL);

    // Should show active scenario name
    await expect(page.getByText('fixed_latency')).toBeVisible({ timeout: 5000 });
    await expect(page.getByText(/active scenarios/i)).toBeVisible();
  });

  test('disabling scenario removes it from active list', async ({ page, request }) => {
    // Enable via API
    await request.post(`${BACKEND_URL}/api/sim/enable`, {
      data: {
        scenario: 'fixed_latency',
        parameters: { target_route: '/api/sim/scenarios', delay_ms: 100 },
      },
    });

    await page.goto(FRONTEND_URL);

    // Wait for active section
    await expect(page.getByText(/active scenarios/i)).toBeVisible({ timeout: 5000 });

    // Click disable button (× button)
    await page.getByRole('button', { name: /×/i }).first().click();

    // Wait for section to disappear
    await expect(page.getByText(/active scenarios \(1\)/i)).not.toBeVisible({ timeout: 5000 });
  });

  test('should reset all scenarios', async ({ page, request }) => {
    // Enable multiple scenarios via API
    await request.post(`${BACKEND_URL}/api/sim/enable`, {
      data: {
        scenario: 'fixed_latency',
        parameters: { target_route: '/api/sim/scenarios', delay_ms: 100 },
      },
    });

    await page.goto(FRONTEND_URL);

    // Active banner should show 1 scenario
    await expect(page.getByText(/1 active scenario/i)).toBeVisible({ timeout: 5000 });

    // Click reset all
    await page.getByRole('button', { name: /reset all/i }).click();

    // Active banner should disappear
    await expect(page.getByText(/1 active scenario/i)).not.toBeVisible({ timeout: 5000 });
  });

  test('should handle loading states', async ({ page }) => {
    await page.goto(FRONTEND_URL);

    // Should show available scenarios list after loading
    await expect(page.getByText(/available scenarios/i)).toBeVisible({ timeout: 5000 });
  });
});
