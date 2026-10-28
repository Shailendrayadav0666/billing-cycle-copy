# Evidence Manifest — Unit Test & Coverage — story-1.1

| Field | Value |
|---|---|
| Work unit | Story 1.1 — Frontend unit-test tooling |
| Branch / head | story/1.1-frontend-unit-test-tooling @ 6c0f1a5 (working tree, story changes staged) · base 6c0f1a5 |
| Generated | 2026-10-28T10:26:28Z |
| AIRE version | 1.0 |
| Status | PASS |

## Commands run
| # | Command | Working directory | Exit code |
|---|---|---|---|
| 1 | baseline: `npm run test` and `./venv/Scripts/python -m pytest --version` (no suite) | src/frontend, src/backend | 1, 1 |
| 2 | `npm run test:coverage` (`vitest run --coverage`) | src/frontend (markerFile package.json present) | 0 |
| 3 | changed-lines measurement: `git diff --unified=0 6c0f1a5` plus untracked files, intersected with lcov DA/BRDA records | repository root | 0 |
| 4 | test placement check over the diff | repository root | 0 |
| 5 | full regression: `npm run test -- --reporter=verbose` and `./venv/Scripts/python -m pytest --version` | src/frontend, src/backend | 0, 1 (no backend runner, unchanged) |

## Tools
| Tool | Version |
|---|---|
| Node / npm | v22.14.0 / 10.9.2 |
| vitest | 5.0.5 |
| @vitest/coverage-v8 | 5.0.5 |
| jsdom | 29.1.1 |
| @testing-library/react / @testing-library/dom | 16.3.3 / 10.4.2 |

## Result
| Item | Value |
|---|---|
| Tests passed | 4/4 (tests/unit/frontend/pages/Billing.test.jsx) |
| Changed executable lines covered | 0/0 — no changed file is instrumented: this unit changes no application source under src/frontend/src |
| Changed branches covered | 0/0 |
| Threshold | 90.0% (unitTestCoverageMin) |
| Gate metric (coverage/changed-lines-coverage.json) | lineCoverage 100.0, branchCoverage 100.0, status PASS (no changed executable lines) |
| Whole-file coverage (transparency, not the gate metric) | src/frontend/src/pages/Billing.jsx 100% lines, 87.5% branches (line 137, the counted-usage branch, has no Standard data); all files 24% lines (App.jsx, main.jsx, AuthContext.jsx, Login.jsx untested before and after this unit) |
| Baseline pass/fail | 0 tests — no test suite existed |
| Post-change pass/fail | 4 passed, 0 failed |
| New failures | 0 |
| Test placement verdict | PASS — 0 violations, 0 warnings (test-placement-check.log) |

## Artifacts
| File | What it is |
|---|---|
| baseline-regression.log | whole-repo suite before any change |
| unit-test-run.log | raw output of the final passing `npm run test:coverage` run |
| coverage/lcov.info | machine-readable coverage report (lcov) |
| coverage/coverage-summary.json | coverage summary (json-summary reporter) |
| coverage/lcov-report/ | HTML coverage report |
| coverage/changed-lines-coverage.json | the gate metric: coverage of changed lines and branches |
| full-regression.log | whole-repo suite after the change, with the diff against the baseline |
| test-placement-check.log | placement of every changed test file |

## Exceptions and notes
- Changed files are configuration (package.json, package-lock.json, vitest.config.js, .gitignore), documentation (README.md), the unit test, and the behaviour and eval tooling under tests/. None is application source covered by coverage.include (src/**/*.{js,jsx}), so the changed-lines metric has no lines to measure. The tooling the unit adds is proven by the 4 passing tests and by B1 (AC-2, AC-3).
- `/api/billing` is mocked in every test (`vi.stubGlobal('fetch', ...)`); no request reaches a real endpoint.
- Self-healing: SH-LOOP-1 used 0 attempts; SH-LOOP-3 used 0; SH-LOOP-12 used 0. The first `npm run test` during implementation (before this gate) failed to load the test file from outside the Vite root; that was an implementation step, fixed by Plan Revision R1 (test-only vitest.config.js), not a gate attempt.
