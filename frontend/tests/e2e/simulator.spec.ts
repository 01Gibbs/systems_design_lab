// Playwright E2E test for Simulator Control Panel
// (moved from e2e/ to tests/e2e/)
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

    // Should remove from list
    await expect(page.getByText('fixed_latency')).not.toBeVisible({ timeout: 5000 });
  });
});
