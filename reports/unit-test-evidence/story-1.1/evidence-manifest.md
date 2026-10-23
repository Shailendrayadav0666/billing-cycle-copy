# Evidence Manifest — Unit tests + coverage — story-1.1

| Field | Value |
|---|---|
| Work unit | Story 1.1 — Upgrade to Premium on the Billing page (frontend only) |
| Branch / head | story/1.1-upgrade-to-premium-on-the-billing-page @ e6aa80b (+ uncommitted story changes) · base e6aa80b |
| Generated | 2026-10-23T15:31:30Z |
| AIRE version | 1.0 |
| Status | PASS |

## Commands run
| # | Command | Working directory | Exit code |
|---|---|---|---|
| 1 | `npm test` (baseline; script did not exist) | `src/frontend` | 1 (Missing script: "test") |
| 2 | `npx vitest run --coverage` | `src/frontend` (ci.roots[0]) | 0 |
| 3 | `python changed_cov.py story-1.1 e6aa80b coverage/lcov.info …` (git diff --unified=0 ∩ lcov DA/BRDA) | repo root | 0 |
| 4 | `npm test -- --reporter=verbose` (full regression) | `src/frontend` | 0 |
| 5 | test-placement rules applied to `git diff --name-only --diff-filter=ACMR e6aa80b` + untracked | repo root | 0 |

## Tools
| Tool | Version |
|---|---|
| vitest | 5.0.5 |
| @vitest/coverage-v8 | 5.0.5 |
| jsdom | 29.1.1 |
| @testing-library/react | 16.3.3 |
| node | 22.14.0 |

## Result
| Metric | Value |
|---|---|
| Tests passed | 15/15 |
| Changed executable lines covered | 5/5 (100.0%) |
| Changed branches covered | 4/4 (100.0%) |
| Threshold | 90.0% (`unitTestCoverageMin`) |
| Whole-file coverage, Billing.jsx (transparency, not the gate metric) | 100% lines · 91.66% branches (line 197, pre-existing non-feature usage path) |
| Baseline pass/fail | 0 tests (no suite existed) |
| Post-change pass/fail | 15 passed / 0 failed |
| New failures | 0 |
| Test placement verdict | PASS — 0 violations (`test-placement-check.log`) |

## Artifacts
| File | What it is |
|---|---|
| `baseline-regression.log` | whole-repo suite before any change (no suite) |
| `unit-test-run.log` | raw output of the final passing `vitest run --coverage` |
| `coverage/lcov.info`, `coverage/coverage-final.json`, `coverage/coverage-summary.json`, `coverage/lcov-report/` | v8 coverage tool output |
| `coverage/changed-lines-coverage.json` | gate metric — changed-lines coverage |
| `full-regression.log` | whole-repo suite after the change |
| `test-placement-check.log` | test placement verification |

## Exceptions and notes
- SH-LOOP-1 used 2 of 3 attempts: (1) jsdom 30.1.3 requires node ^22.22.2 (installed 22.14.0) → pinned jsdom 29.1.1; (2) bare imports from repo-root `tests/` could not reach `src/frontend/node_modules` → `resolveFromPackage` plugin in `src/frontend/vitest.shared.js`. Both logged with root cause in the story audit fragment.
