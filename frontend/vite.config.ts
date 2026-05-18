/**
 * Vite configuration for the Test Constructor frontend.
 * Alias @/src is preserved; vite-plugin-wasm enables .wasm imports.
 */
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import wasm from 'vite-plugin-wasm'
import path from 'path'

export default defineConfig({
  plugins: [react(), wasm()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8023',
        changeOrigin: true,
      },
    },
    host: '0.0.0.0',
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './vitest.setup.ts',
    include: ['src/**/*.{test,spec}.{ts,tsx}'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
    },
  },
})
