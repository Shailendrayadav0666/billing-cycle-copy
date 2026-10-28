import { fileURLToPath } from 'node:url'
import { defineConfig, mergeConfig } from 'vitest/config'
import viteConfig from './vite.config.js'

// The unit tests live outside this folder, under tests/unit/frontend/ (mirroring src/).
const unitTestsDir = fileURLToPath(new URL('../../tests/unit/frontend', import.meta.url))

export default mergeConfig(
  viteConfig,
  defineConfig({
    // Test runs only: let Vitest load the test files, and make their imports
    // resolve to this project's single copy of each package.
    server: {
      fs: {
        allow: ['.', unitTestsDir],
      },
    },
    resolve: {
      dedupe: [
        'react',
        'react-dom',
        'react-router-dom',
        '@testing-library/react',
        '@testing-library/dom',
        'vitest',
      ],
    },
    test: {
      environment: 'jsdom',
      dir: unitTestsDir,
      include: ['**/*.test.{js,jsx}'],
      coverage: {
        provider: 'v8',
        reporter: ['text', 'lcov', 'json-summary'],
        reportsDirectory: 'coverage',
        include: ['src/**/*.{js,jsx}'],
      },
    },
  }),
)
