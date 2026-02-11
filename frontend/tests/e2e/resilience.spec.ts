import { test, expect } from '@playwright/test';
const BACKEND_URL = 'http://localhost:8000';
const FRONTEND_URL = 'http://localhost:5173';

test.describe('Simulator Control Panel - Resilience', () => {
  test('UI remains responsive under slow API', async ({ page, request }) => {
    // Enable fixed latency scenario
    await request.post(`${BACKEND_URL}/api/sim/enable`, {
      data: {
        name: 'fixed_latency',
        parameters: { target_route: '/api/sim/scenarios', delay_ms: 2000 },
      },
    });
    await page.goto(FRONTEND_URL);
    // UI should show loading indicator, not freeze
    await expect(page.getByText(/loading/i)).toBeVisible();
    // After delay, scenarios should load
    await expect(page.getByText(/scenarios/i)).toBeVisible({ timeout: 5000 });
  });
});
