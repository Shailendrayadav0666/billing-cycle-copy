import react from '@vitejs/plugin-react'
import { quickpickle } from 'quickpickle'
import { defineConfig } from 'vitest/config'
import { repoRoot, resolveFromPackage } from './vitest.shared.js'

// Gherkin behaviour specs (QuickPickle). Feature files are passed explicitly through AIRE_FEATURES
// (comma-separated, repo-root relative) by tests/.evals/behavior/run.sh; by default every work-unit
// contract in spec/behavior/ runs. Step definitions live in the repo-root tests/behavior/steps/.
const features = (process.env.AIRE_FEATURES || 'spec/behavior/*.feature')
  .split(',')
  .filter(Boolean)
  .map((f) => `../../${f.trim()}`)

export default defineConfig({
  plugins: [resolveFromPackage(), react(), quickpickle({ stepTimeout: 10000 })],
  server: { fs: { allow: [repoRoot] } },
  test: {
    include: features,
    environment: 'jsdom',
    css: true,
    fileParallelism: false,
    setupFiles: ['../../tests/unit/setup.js', '../../tests/behavior/steps/billing.steps.jsx'],
    testTimeout: 300000,
    // quickpickle's ESM build imports 'pngjs/browser' without an extension; inlining it lets Vite resolve it.
    server: { deps: { inline: ['quickpickle'] } },
  },
})
