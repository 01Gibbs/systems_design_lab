//jest.setup.cjs - Environment polyfills (runs before test framework initialization)

// Set process.env for Jest (Vite uses process.env through client.ts fallback)
process.env.VITE_API_URL = process.env.VITE_API_URL || 'http://localhost:8000';

// Polyfill Web Streams for MSW (jsdom doesn't expose them in sandboxed environment)
// MSW imports modules expecting these at import time (e.g., src/core/sse.ts)
const { ReadableStream, WritableStream, TransformStream } = require('node:stream/web');
Object.assign(globalThis, {
  ReadableStream,
  WritableStream,
  TransformStream,
});

// Polyfill TextEncoder/TextDecoder for jsdom (required by MSW)
if (typeof globalThis.TextEncoder === 'undefined') {
  const { TextEncoder, TextDecoder } = require('util');
  globalThis.TextEncoder = TextEncoder;
  globalThis.TextDecoder = TextDecoder;
}

// Polyfill BroadcastChannel for MSW (jsdom doesn't include it)
if (typeof globalThis.BroadcastChannel === 'undefined') {
  // Minimal BroadcastChannel implementation for testing
  globalThis.BroadcastChannel = class BroadcastChannel {
    constructor(name) {
      this.name = name;
    }
    postMessage() {}
    close() {}
    addEventListener() {}
    removeEventListener() {}
  };
}
