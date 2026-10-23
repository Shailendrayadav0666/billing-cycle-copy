# Code Generation Plan: Story 1.1 Upgrade to Premium on the Billing page (frontend only)

**Story**: 1.1 (LOCAL) · **Epic**: Atlas document 7344 · **Branch**: `story/1.1-upgrade-to-premium-on-the-billing-page` (cut from `epic/7344-premium-upgrade-demo-frontend-only` @ e6aa80b)
**Covers**: REQ-F-01..REQ-F-10, REQ-NF-01..REQ-NF-06 · **Requires**: none · **Enables**: none
**Code root**: `src/` (brownfield; no `## Code Root` override) · **Manifest root**: `src/frontend` (`tests/.evals/config.json` `ci.roots[0]`)
**Generated**: 2026-10-23T15:02:25Z · **AIRE**: v1.0
**This plan is the single source of truth for Story 1.1's code generation.** It was announced and executed with no approval gate.

## Context
- **Acceptance criteria**: `spec/plans/stories.md` Story 1.1, AC-1 to AC-10
- **Behaviour contract**: `spec/behavior/story-1.1.feature` (16 scenarios, approved at the STOP CHECKPOINT). It is read, never rewritten.
- **Architecture constraints**: `spec/plans/architecture.md` Section 10, ARCH-01 to ARCH-06
- **Existing system**: `spec/plans/atlas-deep-dive.md` Flow 4 (Billing fetches `GET /api/billing` once on mount)
- **Design reference**: Atlas story doc 7342 is grounded for the `Billing` component (`PREMIUM_DATA` values, `handleUpgrade` merge keeping `renew_at`, placement below the plan row, `upgrade-btn` / `upgrade-success` classes). Reconciled points from `### Reconciliations` (settled, not reopened): labels are data-driven (Q1 = A); the button is auto width (Q3 = B); the story header's epic name is not followed (Q7 = A).
- **UI/UX standards**: N/A. UI/UX Mockups = No, so `common/ui-ux-design-standards.md` is not applied.
- **Deviation from design reference (DR-6, recorded)**: Atlas doc 7342 suggests `color: #16a34a` for the success message. That colour gives about 3.3:1 contrast on white, which fails REQ-NF-03 / TC-A11Y-04 (4.5:1 or more). The plan uses `#15803d` (Tailwind green-700, about 5.0:1). The AC sets no colour, so no AC is amended.
- **Additional repo instruction**: the user's global instruction "create a readme file for the code" is covered by Step 6.

## Steps

- [x] **Step 1: Frontend unit-test tooling** (REQ-NF-04, REQ-NF-05, AC-10)
  - `src/frontend/package.json`: add **devDependencies only**, exact-pinned: `vitest` 5.0.5, `@vitest/coverage-v8` 5.0.5, `jsdom` 30.1.3, `@testing-library/react` 16.3.3, `@testing-library/dom` 10.4.2, `@testing-library/jest-dom` 7.0.1, `@testing-library/user-event` 14.6.8, `quickpickle` 1.11.2 (the Gherkin runner for the behaviour gate) and `pixelmatch` 6.0.0 (QuickPickle's peer). Add scripts `test`, `test:coverage` and `test:behavior`. Update `package-lock.json` via npm from the official registry.
  - `src/frontend/vitest.config.js`: jsdom environment; include `../../tests/unit/**/*.test.{js,jsx}`; setup file `../../tests/unit/setup.js`; v8 coverage with lcov, json-summary and html reporters into `coverage/`, measured on `src/**`.
  - `tests/unit/setup.js`: jest-dom matchers and RTL cleanup.
- [x] **Step 2: Data-driven plan labels** (REQ-F-05, REQ-F-09, AC-3; ARCH-03)
  - In `Billing.jsx`, the current-plan badge renders `{data.plan_name}` and keeps the `standard-badge` class (teal styling). The heading becomes `What's included with {data.plan_name}`.
- [x] **Step 3: Premium data constant and upgrade handler** (REQ-F-03, REQ-F-04, REQ-NF-01, REQ-F-10, AC-4, AC-5, AC-7; ARCH-01, ARCH-02, ARCH-04)
  - Add a module-level `PREMIUM_DATA` constant to `Billing.jsx` with the exact values from Atlas doc 7342 and REQ-F-03.
  - Add an `upgraded` state and `handleUpgrade`: `setData((prev) => ({ ...prev, ...PREMIUM_DATA, renew_at: prev.renew_at }))` followed by `setUpgraded(true)`. There is no fetch, storage or navigation.
- [x] **Step 4: Upgrade button and success message** (REQ-F-01, REQ-F-02, REQ-F-06, REQ-F-07, REQ-F-08, REQ-NF-03, AC-1, AC-2, AC-6, AC-8)
  - Below the `plan-row` div and before the `section-title`, render the button only when `data.plan_name === 'Standard'`: a native `<button type="button" className="btn upgrade-btn" data-testid="billing-upgrade-button">Upgrade to Premium</button>`.
  - When `upgraded` is true, render `<p className="upgrade-success" role="status" data-testid="billing-upgrade-success">You're now on Premium!</p>`.
- [x] **Step 5: Styles** (REQ-F-08, REQ-F-06, REQ-NF-03, AC-1, AC-6, AC-8)
  - `App.css`: `.upgrade-btn` (`width: auto; margin-top: 1rem; padding: 0.7rem 1.4rem;`) and `.upgrade-btn:focus-visible` (a visible 3px outline with offset).
  - `.upgrade-success` (`margin-top: 0.75rem; color: #15803d; font-weight: 500;`).
- [x] **Step 6: Documentation** (REQ-NF-04; user instruction "create a readme file for the code")
  - Replace the Vite template text in `src/frontend/README.md` with a StreamPlex frontend README covering: run, build, lint, the unit-test and behaviour-test commands, and the Billing page "Upgrade to Premium" demo (local state only; a refresh resets it).
- [x] **Step 7: Unit Test & Coverage** (Step 11a, SH-LOOP-1; all ACs; REQ-NF-02 regression characterization)
  - `tests/unit/pages/Billing.test.jsx` (mirrors `src/pages/`) uses a mocked `fetch` and covers AC-1 to AC-9: loading state, Standard display unchanged, labels, button visible / hidden (Standard, Premium, Basic), click switches the data, `renew_at` preserved, success message `role="status"`, button removed, exactly one fetch, keyboard activation, and remount re-fetches Standard.
  - Run `npx vitest run --coverage`. Capture `unit-test-run.log`, the coverage output and `changed-lines-coverage.json`, and require at least `unitTestCoverageMin` on changed lines.
- [x] **Step 8: Behavioural Gate B1/B2/B3** (Step 6.1, SH-LOOP-7 and 8; AC-1 to AC-10; REQ tags in `spec/behavior.feature`)
  - Write step definitions in `tests/behavior/steps/billing.steps.jsx`, bound to the rendered Billing page (its public UI surface) with a stubbed `/api/billing`.
  - Add `src/frontend/vitest.behavior.config.js` (QuickPickle; features `spec/behavior/*.feature`, plus `spec/behavior.feature` for B3).
  - Add the runner image `tests/.evals/behavior/Containerfile` (node 22) and `tests/.evals/behavior/run.sh <b1|b2|b3>`, run in Podman.
  - Expected outcomes:
    - B1: story-1.1.feature.
    - B2: N/A, because the repo holds no other feature file.
    - B3: runs, because this is the single, and therefore last, work unit. It covers `spec/behavior.feature`, whose login, upgrade and reload journey is bound through the SPA's public surface (`App` with a stubbed backend).
- [x] **Step 9: API & Contract Testing Gate**: **N/A**. The plan has no API Layer Generation step (REQ-NF-01; ARCH-05).
- [x] **Step 10: Test Placement Verification** (Step 6.3, SH-LOOP-12). Check the diff for test files, expecting `tests/unit/pages/`, `tests/unit/setup.js` and `tests/behavior/steps/`, with none under `src/`. Write `test-placement-check.log`.
- [x] **Step 11: Full Regression** (Step 6.5, SH-LOOP-3; REQ-NF-02, AC-9). Run the entire suite (unit and behaviour) into `full-regression.log`, diffed against the baseline (0 tests).
- [x] **Step 12: Static Eval D1 to D7** (Step 6.6, SH-LOOP-4). Re-run oxlint, semgrep, npm audit, the licence checker, ESLint complexity and gitleaks (D2 is N/A for plain JSX). Count only NEW findings on changed files. Then write `eval.json` and `eval-summary.md`.
- [x] **Step 13: Test Plan Verification** (Step 6.7). Confirm that `spec/test-plans/story-1.1-upgrade-to-premium-on-the-billing-page/` is present, was approved at the STOP CHECKPOINT and covers 10/10 ACs. No backfill is needed.

## Trace Summary (Rule 5 self-check)

| REQ / AC | Plan steps |
|---|---|
| REQ-F-01 / AC-1 | 4, 5, 7, 8 |
| REQ-F-02 / AC-2 | 4, 7, 8 |
| REQ-F-03 / AC-4 | 3, 7, 8 |
| REQ-F-04 / AC-5 | 3, 7, 8 |
| REQ-F-05 / AC-3, AC-6 | 2, 4, 7, 8 |
| REQ-F-06 / AC-6 | 4, 5, 7, 8 |
| REQ-F-07 / AC-6 | 4, 7, 8 |
| REQ-F-08 / AC-1 | 4, 5, 7 |
| REQ-F-09 / AC-3 | 2, 7 |
| REQ-F-10 / AC-7 | 3, 7, 8 |
| REQ-NF-01 / AC-7 | 3, 7, 8, 9 |
| REQ-NF-02 / AC-9 | 7, 8, 11 |
| REQ-NF-03 / AC-8 | 4, 5, 7, 8 |
| REQ-NF-04 / AC-10 | 1, 6, 7 |
| REQ-NF-05 / AC-10 | 1, 12 |
| REQ-NF-06 / AC-9 | 2 to 5 (production changes confined to `Billing.jsx` and `App.css`) |

**Self-check**: 16/16 REQ-IDs and 10/10 ACs appear in at least one step. PASS.

## Execution notes
- Step 1 deviation (recorded): jsdom pinned 29.1.1 instead of 30.1.3 (engine: node 22.14.0); `src/frontend/vitest.shared.js` added so repo-root tests resolve this package's dependencies.
- Step 8: QuickPickle needed `server.deps.inline`; `package-lock.json` removed from `src/frontend/.gitignore` (REQ-NF-05); `coverage` added to it.
- Step 9 N/A, Step 13 verified present. All steps complete.
