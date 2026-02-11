/**
 * Typed API Client - Contract-First
 *
 * Types are generated from ../openapi.json (backend snapshot).
 * DO NOT mirror API contracts with Zod here.
 *
 * To regenerate types: npm run contracts:gen
 */

import type { components } from './types';

// Type aliases from generated OpenAPI types
export type Scenario = components['schemas']['ScenarioDescriptor'];
export type ActiveScenario = components['schemas']['ActiveScenario'];
export type ScenariosResponse = components['schemas']['ScenariosResponse'];
export type StatusResponse = components['schemas']['StatusResponse'];

// Support Jest and Node environments where import.meta.env is not available
function getViteEnvUrl(): string | undefined {
  // Only call this in browser context
  // Use new Function to hide import.meta from Jest/Node parser
  try {
    const fn = new Function(
      'return typeof import !== "undefined" && import.meta && import.meta.env ? import.meta.env.VITE_API_URL : undefined'
    );
    return fn();
  } catch {
    return undefined;
  }
}

function getBaseUrl(): string {
  // 1. Node/Jest env - check process.env first
  if (
    typeof process !== 'undefined' &&
    process.env &&
    typeof process.env.VITE_API_URL === 'string'
  ) {
    return process.env.VITE_API_URL;
  }
  // 2. Vite env (browser) - use dynamic function to avoid Jest parse errors
  if (typeof window !== 'undefined') {
    const viteUrl = getViteEnvUrl();
    if (viteUrl) return viteUrl;
  }
  // 3. Default fallback
  return 'http://localhost:8000';
}

const BASE_URL = getBaseUrl();

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

/**
 * Central API client - all components MUST use this, not fetch directly
 */
export const simApi = {
  scenarios: () => request<ScenariosResponse>('/api/sim/scenarios'),

  status: () => request<StatusResponse>('/api/sim/status'),

  enable: (name: string, parameters: Record<string, unknown>, duration_seconds?: number) =>
    request('/api/sim/enable', {
      method: 'POST',
      body: JSON.stringify({ name, parameters, duration_seconds }),
    }),

  disable: (name: string) =>
    request('/api/sim/disable', {
      method: 'POST',
      body: JSON.stringify({ name }),
    }),

  reset: () => request('/api/sim/reset', { method: 'POST' }),
};
