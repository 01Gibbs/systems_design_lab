// Vitest setup file
import '@testing-library/jest-dom';
import { cleanup } from '@testing-library/react';
import { afterEach, beforeAll } from 'vitest';

// Setup React 18 testing environment to avoid concurrent rendering issues
declare global {
  // eslint-disable-next-line no-var
  var IS_REACT_ACT_ENVIRONMENT: boolean | undefined;
}
beforeAll(() => {
  // Enable React testing library act warnings
  globalThis.IS_REACT_ACT_ENVIRONMENT = true;
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
