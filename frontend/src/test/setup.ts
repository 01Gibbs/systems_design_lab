// Vitest setup file
import '@testing-library/jest-dom';
import { cleanup } from '@testing-library/react';
import { afterEach, beforeAll, beforeEach } from 'vitest';

// Setup React 18 testing environment to avoid concurrent rendering issues
declare global {
  // eslint-disable-next-line no-var
  var IS_REACT_ACT_ENVIRONMENT: boolean | undefined;
}

beforeAll(() => {
  // Enable React testing library act warnings
  globalThis.IS_REACT_ACT_ENVIRONMENT = true;
});

beforeEach(() => {
  // Polyfill window.event for React DOM's getCurrentEventPriority
  // React DOM checks if window.event is undefined, but jsdom doesn't define it
  if (typeof window !== 'undefined') {
    try {
      // @ts-expect-error - window.event is a legacy property
      delete window.event;
      Object.defineProperty(window, 'event', {
        get: () => undefined,
        set: () => {
          /* noop */
        },
        configurable: true,
      });
    } catch {
      // Ignore if property already exists and can't be redefined
    }
  }
});

// Cleanup after each test case with proper error handling
afterEach(async () => {
  try {
    cleanup();
  } catch (error) {
    // Ignore cleanup errors that might be caused by React concurrent features
    console.warn('Test cleanup warning:', error);
  }
});
