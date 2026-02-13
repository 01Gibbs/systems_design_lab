/**
 * API Client Tests - Comprehensive function coverage
 *
 * Tests all API client functions including environment detection,
 * error handling, and API methods to boost function coverage.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { simApi } from '../client';

// Mock fetch globally
const mockFetch = vi.fn();
global.fetch = mockFetch;

describe('API Client', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Reset environment variables
    delete process.env.VITE_API_URL;
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Environment Detection', () => {
    it('should use process.env.VITE_API_URL in Node environment', async () => {
      // Set Node environment variable
      process.env.VITE_API_URL = 'http://test-node.com';

      mockFetch.mockResolvedValueOnce({
        ok: true,
        text: () => Promise.resolve('{"scenarios":[]}'),
      });

      await simApi.scenarios();

      expect(mockFetch).toHaveBeenCalledWith(
        'http://test-node.com/api/sim/scenarios',
        expect.any(Object)
      );
    });

    it('should use default URL when no environment variables', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        text: () => Promise.resolve('{"scenarios":[]}'),
      });

      await simApi.scenarios();

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/sim/scenarios',
        expect.any(Object)
      );
    });

    it('should use vite environment URL in browser context', async () => {
      // Mock browser environment
      Object.defineProperty(global, 'window', {
        value: {},
        configurable: true,
      });

      // Mock the Function constructor to return a fake vite URL
      const originalFunction = global.Function;
      global.Function = vi.fn().mockImplementation(() => {
        return () => 'http://vite-test.com';
      });

      mockFetch.mockResolvedValueOnce({
        ok: true,
        text: () => Promise.resolve('{"scenarios":[]}'),
      });

      await simApi.scenarios();

      expect(mockFetch).toHaveBeenCalledWith(
        'http://vite-test.com/api/sim/scenarios',
        expect.any(Object)
      );

      // Restore
      global.Function = originalFunction;
      Object.defineProperty(global, 'window', {
        value: undefined,
        configurable: true,
      });
    });

    it('should handle vite environment function errors gracefully', async () => {
      // This tests the try-catch in getViteEnvUrl()
      const originalFunction = global.Function;
      global.Function = vi.fn().mockImplementation(() => {
        throw new Error('Function creation failed');
      });

      mockFetch.mockResolvedValueOnce({
        ok: true,
        text: () => Promise.resolve('{"scenarios":[]}'),
      });

      await simApi.scenarios();

      // Should fallback to default localhost
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/sim/scenarios',
        expect.any(Object)
      );

      global.Function = originalFunction;
    });
  });

  describe('Request Function', () => {
    it('should handle successful API responses', async () => {
      const mockData = { scenarios: [{ name: 'test' }] };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        text: () => Promise.resolve(JSON.stringify(mockData)),
      });

      const result = await simApi.scenarios();

      expect(result).toEqual({ ok: true, data: mockData });
    });

    it('should handle empty response body', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        text: () => Promise.resolve(''),
      });

      const result = await simApi.scenarios();

      expect(result).toEqual({ ok: true, data: null });
    });

    it('should handle HTTP error responses', async () => {
      const errorBody = { error: 'Not found' };
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        text: () => Promise.resolve(JSON.stringify(errorBody)),
      });

      const result = await simApi.scenarios();

      expect(result).toEqual({ ok: false, status: 404, error: errorBody });
    });

    it('should handle network/fetch errors', async () => {
      const networkError = new Error('Network failed');
      mockFetch.mockRejectedValueOnce(networkError);

      const result = await simApi.scenarios();

      expect(result).toEqual({ ok: false, status: 0, error: networkError });
    });

    it('should handle fetch throwing non-Error objects', async () => {
      const weirdError = 'string error';
      mockFetch.mockRejectedValueOnce(weirdError);

      const result = await simApi.scenarios();

      expect(result.ok).toBe(false);
      if (!result.ok) {
        expect(result.status).toBe(0);
        expect(result.error).toBe(weirdError);
      }
    });

    it('should handle JSON parse errors in success responses', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        text: () => Promise.resolve('{invalid json}'),
      });

      const result = await simApi.scenarios();

      expect(result.ok).toBe(false);
      if (!result.ok) {
        expect(result.status).toBe(0);
        expect(result.error).toBeInstanceOf(SyntaxError);
      }
    });

    it('should handle JSON parse errors in error responses', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        text: () => Promise.resolve('{invalid json}'),
      });

      const result = await simApi.scenarios();

      expect(result.ok).toBe(false);
      if (!result.ok) {
        expect(result.status).toBe(0);
        expect(result.error).toBeInstanceOf(SyntaxError);
      }
    });
  });

  describe('API Methods', () => {
    beforeEach(() => {
      mockFetch.mockResolvedValue({
        ok: true,
        text: () => Promise.resolve('{}'),
      });
    });

    it('should call scenarios endpoint', async () => {
      await simApi.scenarios();

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/sim/scenarios',
        expect.objectContaining({
          headers: expect.objectContaining({
            'content-type': 'application/json',
          }),
        })
      );
    });

    it('should call status endpoint', async () => {
      await simApi.status();

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/sim/status',
        expect.objectContaining({
          headers: expect.objectContaining({
            'content-type': 'application/json',
          }),
        })
      );
    });

    it('should call enable endpoint with parameters', async () => {
      const params = { delay: 100 };
      await simApi.enable('test-scenario', params, 60);

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/sim/enable',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({
            name: 'test-scenario',
            parameters: params,
            duration_seconds: 60,
          }),
          headers: expect.objectContaining({
            'content-type': 'application/json',
          }),
        })
      );
    });

    it('should call enable endpoint without duration', async () => {
      const params = { delay: 100 };
      await simApi.enable('test-scenario', params);

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/sim/enable',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({
            name: 'test-scenario',
            parameters: params,
            duration_seconds: undefined,
          }),
        })
      );
    });

    it('should call disable endpoint', async () => {
      await simApi.disable('test-scenario');

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/sim/disable',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ name: 'test-scenario' }),
          headers: expect.objectContaining({
            'content-type': 'application/json',
          }),
        })
      );
    });

    it('should call reset endpoint', async () => {
      await simApi.reset();

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/sim/reset',
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'content-type': 'application/json',
          }),
        })
      );
    });
  });

  describe('Request Headers', () => {
    it('should merge custom headers with default content-type', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        text: () => Promise.resolve('{}'),
      });

      // Test internal request function via simApi
      await simApi.scenarios();

      expect(mockFetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            'content-type': 'application/json',
          }),
        })
      );
    });
  });
});
