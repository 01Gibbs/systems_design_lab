/**
 * Typed API Client - Contract-First
 *
 * Types are generated from ../openapi.json (backend snapshot).
 * DO NOT mirror API contracts with Zod here.
 *
 * To regenerate types: npm run contracts:gen
 */

import type { paths, components } from './types';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

type ApiResult<T> = { ok: true; data: T } | { ok: false; status: number; error: unknown };

async function request<T>(path: string, init?: RequestInit): Promise<ApiResult<T>> {
  try {
    const res = await fetch(`${BASE_URL}${path}`, {
      ...init,
      headers: {
        'content-type': 'application/json',
        ...(init?.headers ?? {}),
      },
    });

    const text = await res.text();
    const body = text ? JSON.parse(text) : null;

    if (!res.ok) {
      return { ok: false, status: res.status, error: body };
    }

    return { ok: true, data: body as T };
  } catch (e) {
    return { ok: false, status: 0, error: e };
  }
}

// Type aliases from generated schema
export type Scenario = components['schemas']['Scenario'];
export type ActiveScenario = components['schemas']['ActiveScenario'];
export type ScenariosResponse =
  paths['/api/sim/scenarios']['get']['responses'][200]['content']['application/json'];
export type StatusResponse =
  paths['/api/sim/status']['get']['responses'][200]['content']['application/json'];

/**
 * Central API client - all components MUST use this, not fetch directly
 */
export const simApi = {
  scenarios: () => request<ScenariosResponse>('/api/sim/scenarios'),

  status: () => request<StatusResponse>('/api/sim/status'),

  enable: (scenario: string, parameters: Record<string, unknown>) =>
    request('/api/sim/enable', {
      method: 'POST',
      body: JSON.stringify({ scenario, parameters }),
    }),

  disable: (scenario: string) =>
    request('/api/sim/disable', {
      method: 'POST',
      body: JSON.stringify({ scenario }),
    }),

  reset: () => request('/api/sim/reset', { method: 'POST' }),
};
