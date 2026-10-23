import react from '@vitejs/plugin-react'
import { defineConfig } from 'vitest/config'
import { repoRoot, resolveFromPackage } from './vitest.shared.js'

// Unit tests: repo-root tests/unit/ (jsdom + React Testing Library), coverage measured on src/.
export default defineConfig({
  plugins: [resolveFromPackage(), react()],
  server: { fs: { allow: [repoRoot] } },
  test: {
    dir: '../../tests/unit',
    include: ['../../tests/unit/**/*.test.{js,jsx}'],
    environment: 'jsdom',
    setupFiles: ['../../tests/unit/setup.js'],
    passWithNoTests: true,
    coverage: {
      provider: 'v8',
      include: ['src/**/*.{js,jsx}'],
      reporter: ['text', 'lcov', 'json-summary', 'json', 'html'],
      reportsDirectory: 'coverage',
    },
  },
})
