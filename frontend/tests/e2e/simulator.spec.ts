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

    // Enable via API (not UI clicks) using contract-first shape
    await request.post(`${BACKEND_URL}/api/sim/enable`, {
      data: {
        name: 'fixed-latency',
        parameters: {
          ms: 100,
          // Apply latency to simulator HTTP endpoints
          path_prefix: '/api/sim',
          method: 'GET',
        },
      },
    });

    // Wait for banner to appear (polls every 2s)
    await expect(page.getByText(/1 active scenario/i)).toBeVisible({ timeout: 10000 });
  });

  test('page lists scenario name after enable', async ({ page, request }) => {
    // Enable via API
    await request.post(`${BACKEND_URL}/api/sim/enable`, {
      data: {
        name: 'fixed-latency',
        parameters: {
          ms: 100,
          path_prefix: '/api/sim',
          method: 'GET',
        },
      },
    });

    await page.goto(FRONTEND_URL);

    // Should show active scenario name
    await expect(
      page.getByRole('heading', {
        name: 'fixed-latency',
      })
    ).toBeVisible({ timeout: 10000 });
    await expect(page.getByText(/active scenarios/i)).toBeVisible();
  });

  test('disabling scenario removes it from active list', async ({ page, request }) => {
    // Enable via API
    await request.post(`${BACKEND_URL}/api/sim/enable`, {
      data: {
        name: 'fixed-latency',
        parameters: {
          ms: 100,
          path_prefix: '/api/sim',
          method: 'GET',
        },
      },
    });

    await page.goto(FRONTEND_URL);

    // Wait for active section
    await expect(page.getByText(/active scenarios/i)).toBeVisible({ timeout: 5000 });

    // Click disable button (× button)
    const disableButton = page.getByRole('button', { name: /Disable fixed-latency/i });
    await expect(disableButton).toBeVisible({ timeout: 10000 });
    await disableButton.click();

    // Should remove from active list - check specifically that disable button is gone
    await expect(page.getByRole('button', { name: /Disable fixed-latency/i })).not.toBeVisible({
      timeout: 10000,
    });
  });
});
