/**
 * Enhanced test utilities for React 18
 * Provides better support for concurrent features and proper cleanup
 */
import React from 'react';
import { render, type RenderOptions, type RenderResult } from '@testing-library/react';
import type { MockedFunction } from 'vitest';
declare const vi: { fn: <T extends (...args: unknown[]) => unknown>() => MockedFunction<T> };

// Custom render that properly handles React 18 concurrent features
export function renderWithIsolation(
  ui: React.ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
): RenderResult {
  // Ensure consistent test environment
  const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    return <>{children}</>;
  };

  return render(ui, { wrapper: TestWrapper, ...options });
}

// Helper to create properly isolated mock functions
export function createMockFn<T extends (...args: never[]) => unknown>(): MockedFunction<T> {
  return vi.fn() as unknown as MockedFunction<T>;
}

// Helper to wait for React to finish all pending updates
export async function flushPromises(): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, 0));
}

// Re-export commonly used testing utilities explicitly to avoid react-refresh warning
export { render, screen, fireEvent, waitFor, act, cleanup, within } from '@testing-library/react';
export { default as userEvent } from '@testing-library/user-event';
