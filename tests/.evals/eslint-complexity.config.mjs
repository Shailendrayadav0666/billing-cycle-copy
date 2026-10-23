// AIRE D6 complexity gate (bootstrap, eval-framework.md Section 2.3).
// The repo lints with oxlint, which has no cyclomatic-complexity rule, so this config runs ONLY
// ESLint's core `complexity` rule at thresholds.maxCyclomaticComplexity from tests/.evals/config.json.
export default [
  {
    files: ['**/*.{js,jsx}'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      parserOptions: { ecmaFeatures: { jsx: true } },
    },
    linterOptions: { reportUnusedDisableDirectives: 'off' },
    rules: { complexity: ['error', 12] },
  },
]
