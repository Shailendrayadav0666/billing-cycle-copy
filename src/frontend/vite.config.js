import { fileURLToPath, URL } from 'node:url'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [react()],
  esbuild: {
    // Vitest's SSR/node transform pipeline for out-of-root test files does not always apply
    // @vitejs/plugin-react's automatic JSX runtime injection; this guarantees `React` is in
    // scope for JSX in both app and test code without changing any component's own imports.
    jsxInject: "import React from 'react'",
  },
  resolve: {
    alias: {
      // Test files live under the repo-root tests/ tree (common/directory-structure.md), outside
      // this Vite root's own node_modules resolution walk — alias the bare specifiers they need.
      '@testing-library/jest-dom/vitest': fileURLToPath(
        new URL('./node_modules/@testing-library/jest-dom/vitest.js', import.meta.url),
      ),
      '@testing-library/react': fileURLToPath(new URL('./node_modules/@testing-library/react', import.meta.url)),
      react: fileURLToPath(new URL('./node_modules/react', import.meta.url)),
      'react-dom': fileURLToPath(new URL('./node_modules/react-dom', import.meta.url)),
    },
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
    fs: {
      // Allows Vite's dev/test server to read the repo-root tests/ tree (setup file + specs),
      // which lives outside this Vite root (src/frontend) per common/directory-structure.md.
      allow: ['../..'],
    },
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['../../tests/unit/frontend/setup.js'],
    include: ['../../tests/unit/frontend/**/*.test.jsx'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'lcov'],
      reportsDirectory: './coverage',
      include: ['src/pages/Billing.jsx'],
    },
  },
})
