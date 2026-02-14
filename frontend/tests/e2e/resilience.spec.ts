import { test, expect } from '@playwright/test';
const BACKEND_URL = 'http://localhost:8000';
const FRONTEND_URL = 'http://localhost:5173';

test.describe('Simulator Control Panel - Resilience', () => {
  test('UI remains responsive under slow API', async ({ page, request }) => {
    // Enable fixed latency scenario
    await request.post(`${BACKEND_URL}/api/sim/enable`, {
      data: {
        name: 'fixed-latency',
        parameters: {
          ms: 2000,
          path_prefix: '/api/sim',
          method: 'GET',
        },
      },
    });
    await page.goto(FRONTEND_URL);
    // After delay, scenarios should load (allow extra time for injected latency)
    await expect(page.getByRole('heading', { name: /Available Scenarios/i })).toBeVisible({
      timeout: 10000,
    });
  });
});
