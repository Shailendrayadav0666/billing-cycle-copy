# Code Review - Story 1.1: Frontend unit-test tooling

**Date**: 2026-10-28
**Reviewed By**: REVIEWER (aire)
**Review Number**: 1
**Review Mode**: INITIAL_REVIEW
**Review Target**: Story 1.1
**Status**: APPROVED
**Tracker ID**: — (LOCAL)

## Review Summary
**Components Reviewed**: `src/frontend/package.json`, `src/frontend/package-lock.json`, `src/frontend/vitest.config.js`, `src/frontend/.gitignore`, `src/frontend/README.md`, `tests/unit/frontend/pages/Billing.test.jsx`, `tests/behavior/steps/frontend-tooling.steps.cjs`, `tests/behavior/support/audit-review.cjs`, `tests/.evals/behavior/` (Containerfile, run.sh, resolve-tier.cjs, package.json, package-lock.json), `tests/.evals/oxlint-complexity.json`, `.gitleaks.toml`, `.containerignore`
**Stories in Scope**: 1.1
**Tests Reviewed**: Yes — statically; suite NOT re-run  **Coverage**: 100.0% of changed lines, 0 changed executable lines (from Code Generation's Unit Test & Coverage gate, `reports/unit-test-evidence/story-1.1/coverage/changed-lines-coverage.json` — not re-measured); 4/4 tests passed (`unit-test-run.log`)
**API & Contract Tests**: N/A — no API layer touched (the plan has no API Layer Generation step)
**Static Eval Gate (D1–D7)**: PASS — D1, D3, D4, D5, D6, D7 PASS with 0 new findings; D2 N/A (plain JavaScript) (from the Static Eval Gate — not re-run; `reports/eval-evidence/story-1.1/eval-summary.md`)
**Security Baseline (SECURITY-01…16, diff-scoped)**: 16/16 checked · 4 compliant · 12 N/A · Findings: 0 Blocker / 0 High (blocking) · 0 Medium / 0 Low · 2 pre-existing (dependency advisories, not this change) and 3 Low observations, all advisory → report: `reports/code-security-reviews/story-1.1-security-review-v1.md`
**Judge Gates (blocking — Phase 3.5; never findings)**: J1 Architecture 1.00 (min 0.85) PASS · J2 Security 1.00 (min 0.85) PASS — judge `claude-opus-5-5`, rubric v1.0.0; breakdown in `reports/eval-evidence/story-1.1/judge/`
**Overall Assessment**: All four acceptance criteria and both covered requirements (REQ-NF-05, REQ-NF-06) are met by the code as written. The test libraries are dev-only and pinned in a committed, registry-only lock file; `npm run test` and `npm run test:coverage` work as specified, with `/api/billing` mocked; the `npm audit` result is recorded. Behavioural B1 passed 5/5 scenarios in Podman.

## AC & Requirements Verification

### Story 1.1: Frontend unit-test tooling
| # | AC / Requirement | Verdict | Evidence / Gap |
|---|------------------|---------|----------------|
| AC-1 | `src/frontend/package.json` lists Vitest, React Testing Library and jsdom as devDependencies only; no runtime dependency is added | Met | `src/frontend/package.json:20-29` (devDependencies: vitest, @testing-library/react, jsdom, plus @vitest/coverage-v8 and the required peer @testing-library/dom); `src/frontend/package.json:14-18` dependencies unchanged (react, react-dom, react-router-dom); B1 `@AC-1` passed |
| AC-2 | `npm run test` runs Vitest in a jsdom environment and passes a smoke test that renders the Billing page against a mocked `/api/billing` response | Met | `src/frontend/package.json:11` (`vitest run`); `src/frontend/vitest.config.js:29-31` (jsdom, tests in `tests/unit/frontend`); `tests/unit/frontend/pages/Billing.test.jsx:53` (fetch stubbed), `:62` (jsdom), `:67` (renders Billing, finds "Plan & Billing"), `:75-81` (only the mocked `/api/billing` URL is called); B1 `@AC-2` passed |
| AC-3 | `npm run test:coverage` produces a text summary and an lcov report the unit-test gate can check | Met | `src/frontend/package.json:12` (`vitest run --coverage`); `src/frontend/vitest.config.js:33-36` (v8, reporters text, lcov, json-summary, output `coverage/`); `reports/unit-test-evidence/story-1.1/unit-test-run.log` shows the text table; `coverage/lcov.info` written; B1 `@AC-3` passed |
| AC-4 | Exact resolved versions pinned in the committed `src/frontend/package-lock.json`; `npm audit` result recorded | Met | `src/frontend/package-lock.json` staged for the commit, entries at `:958`, `:978`, `:1088`, `:1442`, `:2302` with exact versions, registry.npmjs.org URLs and sha512 integrity; `src/frontend/.gitignore:10-12` no longer ignores the lock and ignores `coverage`; `reports/eval-evidence/story-1.1/npm-audit-install.json` (no high or critical advisory reaching an added package); B1 `@AC-4` (both scenarios) passed |
| REQ-NF-05 | Vitest, RTL and jsdom as dev dependencies with `test` and `test:coverage` scripts; new behaviour covered to `unitTestCoverageMin`; `/api/billing` mocked, never called for real | Met | Tooling and scripts as AC-1 to AC-3; `/api/billing` stubbed in every test (`Billing.test.jsx:49-54`). The coverage clause for REQ-F-01..12 is assigned to Stories 1.2–1.6 by the Requirements Coverage Matrix (`spec/plans/stories.md`: "1.1 (AC-1, AC-2, AC-3); each later story adds its own unit tests"); this unit's changed-lines coverage gate passed |
| REQ-NF-06 | Official npm registry; pinned in the committed lock file; `npm audit` after install, result recorded; no runtime dependency added | Met | Every one of the 155 lock entries resolves from https://registry.npmjs.org/ with sha512 integrity; lock committed; `npm-audit-install.json` saved after install; dependencies unchanged |

Extension compliance: Security Baseline (enabled, mandatory) — compliant on the changed surface (Phase 2.5). UI/UX Mockups, Resiliency and Property-Based Testing are disabled: N/A.

No Playwright: the diff adds nothing under `tests/e2e/` or `spec/playwright-specs/`, no Playwright agents, and `eval.json` has no `playwright` gate.

## Issues Found
No issues — all acceptance criteria and requirements verified as Met; diff is clean against SECURITY-01…16.

## Security — Advisory (non-blocking)
- ADV-01 (pre-existing) — vite 8.3.0 dev-server advisories, npm audit severity high (GHSA-587h-7wmj-h5pm and five moderate/low), SECURITY-10, `src/frontend/package-lock.json:2224`. vite predates this unit; fix 8.3.5. Recommend `/raise-defect`.
- ADV-02 (pre-existing) — source-map-js 1.2.1, npm audit severity high (GHSA-68fv-2mgg-jv7q), SECURITY-10, transitive. Fix 1.2.2. Recommend `/raise-defect` with ADV-01.
- ADV-03 (Low) — behaviour test image runs as root, SECURITY-09, `tests/.evals/behavior/Containerfile:5`; test-only, never deployed, rootless Podman with `--network none`.
- ADV-04 (Low) — behaviour image base pinned by tag, not digest, SECURITY-13, `tests/.evals/behavior/Containerfile:5`.
- ADV-05 (Low) — `npm audit` is not named in `src/frontend/README.md`'s build instructions, SECURITY-10.

## Issue Summary
| # | ID | Severity | AC/Requirement or SECURITY rule | File | Status |
|---|-----|----------|----------------|------|--------|
| — | — | — | None | — | — |

**Counts**: Blockers: 0 | High: 0 — of which security: 0 Blocker / 0 High · Advisory (non-blocking): 5

## Approval Status
**Decision**: APPROVED
**Reason**: Every acceptance criterion and covered requirement is Met with file:line evidence, there are no Blocker or High security findings on the changed surface, and both judge gates pass (J1 1.00, J2 1.00).
