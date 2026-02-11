// Polyfill import.meta.env for Jest (Vite env compatibility)
if (typeof import !== 'undefined' && import.meta) {
  import.meta.env = import.meta.env || {};
  import.meta.env.VITE_API_URL = process.env.VITE_API_URL || 'http://localhost:8000/api';
} else {
  globalThis.import = { meta: { env: { VITE_API_URL: process.env.VITE_API_URL || 'http://localhost:8000/api' } } };
}