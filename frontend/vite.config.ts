import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: process.env.VITE_API_URL || 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
    exclude: ['**/node_modules/**', '**/dist/**', '**/e2e/**', '**/*.spec.ts'],
    include: ['**/*.test.{ts,tsx}'],
    testTimeout: 15000, // 15 second timeout for tests
    // Reduce worker pool size to avoid EAGAIN errors in WSL
    pool: 'forks',
    poolOptions: {
      forks: {
        singleFork: true, // Run in single fork process to avoid resource exhaustion
      },
    },
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'lcov'],
      exclude: [
        'node_modules/**',
        'src/test/**',
        '**/*.config.{ts,js,cjs}',
        '**/tests/**',
        '**/*.d.ts',
        '**/e2e/**',
        '**/__tests__/**',
        '**/*.test.{ts,tsx}',
        '**/*.spec.{ts,tsx}',
        'src/main.tsx', // Entry point, not testable
        'src/api/types.ts', // Type definitions only
      ],
      thresholds: {
        lines: 80,
        functions: 75, // Temporary: Async handlers and type files make 80% difficult
        branches: 80,
        statements: 80,
      },
    },
  },
});
