# Story 1.1 Code Generation Plan — Frontend unit-test tooling

**Story**: 1.1 — Frontend unit-test tooling (Tracker ID LOCAL)
**Epic**: HELIX-7344 — Premium Upgrade Demo (Frontend Only)
**Branch**: `story/1.1-frontend-unit-test-tooling`, cut from `epic/HELIX-7344-premium-upgrade-demo-frontend-only` at 6c0f1a5
**Covers**: REQ-NF-05, REQ-NF-06
**Requires**: none · **Enables**: 1.2, 1.3, 1.4 (their unit-test gates need this runner)
**AIRE Framework**: v1.0
**Status**: auto-approved (no plan gate) — this file is the single source of truth for Part 2

## Story context

As a product stakeholder, I want the Billing page's behaviour checked by automated unit tests so that the demo works the same way every time it is shown.

| AC | Criterion (from `spec/plans/stories.md`) |
|----|------------------------------------------|
| AC-1 | `src/frontend/package.json` lists Vitest, React Testing Library and jsdom as devDependencies only; no runtime dependency is added. |
| AC-2 | `npm run test` runs Vitest in a jsdom environment and passes a smoke test that renders the Billing page against a mocked `/api/billing` response. |
| AC-3 | `npm run test:coverage` produces a text summary and an lcov report the unit-test gate can check against `unitTestCoverageMin`. |
| AC-4 | The new dev dependencies come from the official npm registry, their exact resolved versions are pinned in the committed `src/frontend/package-lock.json`, and the `npm audit` result is recorded in the story's evidence. |

Requirement text read from `spec/plans/requirements.md`:
- **REQ-NF-05** — Vitest, React Testing Library and jsdom as dev dependencies with `test` and `test:coverage` scripts; new behaviour covered to `unitTestCoverageMin`; `/api/billing` mocked in tests, never called for real.
- **REQ-NF-06** (SECURITY-10) — official npm registry; pinned in the committed lock file; `npm audit` after install, result recorded with the evidence; no runtime dependency added.

Design inputs:
- `spec/plans/architecture.md` Section 3: tests live under `tests/unit/frontend/`, mirroring `src/frontend/src/`; the runner configuration lives in `src/frontend/` and points at that folder.
- `spec/plans/architecture.md` Section 6: `src/frontend/.gitignore` ignores `package-lock.json` today (must be removed) and does not ignore `coverage/` (must be added).
- `spec/plans/architecture.md` Section 10: ARCH-06 (dev-only, pinned test tooling) and ARCH-01 (no backend change, no new network call) apply to this diff.
- `tests/.evals/config.json`: `unitTestCoverageMin` 90; root `src/frontend` runs `npm run test:coverage` and reads `coverage/lcov.info`; `testPaths` `tests/unit/frontend`; runtime Node 22.14.0.
- Design reference: none covers this component (`## Design References` records none) — built from ACs only.
- UI/UX design standards: N/A — UI/UX Mockups not enabled, and no UI is rendered differently by this unit.

Out of scope: any change to `src/frontend/src/**` application code, the backend, or the Billing page's behaviour (Stories 1.2 to 1.6).

## Version decisions

| Package | Version | Why |
|---------|---------|-----|
| vitest | 5.0.5 | latest; supports vite ^8 (the repo runs vite 8.3.0) and Node ^22.12 |
| @vitest/coverage-v8 | 5.0.5 | the coverage provider `vitest run --coverage` needs; must equal the vitest version |
| jsdom | 29.1.1 | newest release whose `engines` accepts Node 22.14.0; jsdom 30.x needs Node ^22.22.2, and the runtime pin is not bumped (behavior-spec.md Section 5.2.1 rule 3) |
| @testing-library/react | 16.3.3 | latest; supports React 19 |
| @testing-library/dom | 10.4.2 | required peer dependency of @testing-library/react 16 |
| @cucumber/cucumber | 13.3.0 | behavioural runner, installed only in the behaviour image (not an app dependency); `engines` accepts Node 22 |

Registry: `npm config get registry` returns `https://registry.npmjs.org/` (official).

## Steps

- [x] **Step 1 — Add the test libraries as dev dependencies** (REQ-NF-05, REQ-NF-06; AC-1, AC-4)
  In `src/frontend/`: `npm install --save-dev vitest@5.0.5 @vitest/coverage-v8@5.0.5 jsdom@29.1.1 @testing-library/react@16.3.3 @testing-library/dom@10.4.2`. Verify `dependencies` still lists only react, react-dom and react-router-dom, and that every new entry in `package-lock.json` resolves from `https://registry.npmjs.org/` with an integrity hash.
- [x] **Step 2 — Run `npm audit` after the install and record it** (REQ-NF-06; AC-4)
  `npm audit --json` in `src/frontend/`, saved to `reports/eval-evidence/story-1.1/npm-audit-install.json`. Any high or critical advisory that reaches a newly added dev dependency is resolved by moving to a non-vulnerable version before the story continues; advisories already present at the baseline are recorded, not fixed here.
- [x] **Step 3 — Add the npm scripts** (REQ-NF-05; AC-2, AC-3)
  `"test": "vitest run"` and `"test:coverage": "vitest run --coverage"` in `src/frontend/package.json`.
- [x] **Step 4 — Configure Vitest in a test-only `src/frontend/vitest.config.js`** (REQ-NF-05; AC-2, AC-3) — *revised during Part 2, see Plan Revisions*
  `vitest.config.js` merges the unchanged `vite.config.js` (React plugin, `/api` proxy) and adds, for test runs only: `server.fs.allow` for `src/frontend` plus `tests/unit/frontend` (Vite refuses to load files outside its workspace root otherwise); `resolve.dedupe` for the packages the tests import, so test files outside `src/frontend/` resolve them from `src/frontend/node_modules`; `test.environment: 'jsdom'`; `test.dir` at `tests/unit/frontend` with `*.test.{js,jsx}` files; coverage provider `v8`, reporters `text`, `lcov` and `json-summary`, output `coverage/`, measured over `src/**/*.{js,jsx}`. `vite.config.js` itself is not modified.
- [x] **Step 5 — Update `src/frontend/.gitignore`** (REQ-NF-06; AC-4)
  Remove the `package-lock.json` entry so the lock file is committed; add `coverage` so generated reports stay uncommitted (architecture.md Section 6).
- [x] **Step 6 — Billing page smoke test** (REQ-NF-05; AC-2)
  `tests/unit/frontend/pages/Billing.test.jsx`, mirroring `src/frontend/src/pages/Billing.jsx`. `useAuth` is mocked with a fixed token, and `fetch` is stubbed so `/api/billing` returns a Standard response (`plan_name` "Standard", `price` "$20/month"). Tests: it runs in jsdom; it renders the Billing page and finds the "Plan & Billing" heading; it calls only the mocked `/api/billing` URL, never a real endpoint; it shows the loading text before the response arrives.
- [x] **Step 7 — Document the test commands** (REQ-NF-05; AC-2, AC-3)
  Add a "Unit tests" section to `src/frontend/README.md`: `npm run test`, `npm run test:coverage`, where the tests live, and that `/api/billing` is always mocked.
- [x] **Step 8 — Unit Test & Coverage gate** (REQ-NF-05; AC-2, AC-3) — code-generation.md Step 11a, SH-LOOP-1
  Run `npm run test:coverage` in `src/frontend/`; save `unit-test-run.log`, the coverage folder (`lcov.info`, `coverage-summary.json`, HTML) and `coverage/changed-lines-coverage.json` to `reports/unit-test-evidence/story-1.1/`, plus `evidence-manifest.md`.
- [x] **Step 9 — Behavioural runner bootstrap and step definitions** (REQ-NF-05, REQ-NF-06; AC-1, AC-2, AC-3, AC-4) — dev-implement Step 6.1, SH-LOOP-7
  First work unit of the cycle, so the runner is bootstrapped: `tests/.evals/behavior/Containerfile` (Node 22.14.0 image; the app's dependencies installed from the committed lock; cucumber-js 13.3.0 from a pinned `tests/.evals/behavior/package.json` and lock), `tests/.evals/behavior/run.sh` (resolves B1, B2 or B3 membership from `spec/` and the Story Tracker), and step definitions in `tests/behavior/steps/` with shared helpers in `tests/behavior/support/`. Steps bind to the project's public surface: `package.json`, the npm scripts, the lock file, git's ignore and index state, the saved audit evidence, and the `dependencyVulnerabilitiesAllowed` threshold in `tests/.evals/config.json`. Run B1 in Podman (`AIRE_STORY_KEY=story-1.1`, no network); B2 and B3 resolve per behavior-spec.md Sections 6.0 and 6.1.
- [x] **Step 10 — API & Contract Testing gate** — N/A: this plan has no API Layer Generation step; Story 1.1 adds no endpoint.
- [x] **Step 11 — Test Placement Verification** (dev-implement Step 6.3, SH-LOOP-12)
  Check the diff: the unit test sits under `tests/unit/frontend/` (mirroring `src/frontend/src/pages/`), no test under `src/`, and nothing under `tests/api/`.
- [x] **Step 12 — Full Regression vs baseline** (dev-implement Step 6.5, SH-LOOP-3)
  Re-run the whole repo suite and diff it against `baseline-regression.log` (baseline: no test suite).
- [x] **Step 13 — Static Eval Gate D1 to D7** (dev-implement Step 6.6, SH-LOOP-4)
  Same tools and configs as the baseline (`static/baseline/`), now including the new test and behaviour files; only NEW findings on changed files count. Write `eval.json` and `eval-summary.md`.
- [x] **Step 14 — Test Plan Verification** (dev-implement Step 6.7)
  `spec/test-plans/story-1.1-frontend-unit-test-tooling/` exists (approved at the STOP CHECKPOINT) and covers AC-1 to AC-4.
- [x] **Step 15 — Deployment artifacts** — none: the change is development tooling only; no build or runtime artifact changes.

## Plan Revisions

| # | Step | What changed | Why |
|---|------|--------------|-----|
| R1 | 4 | Vitest settings moved from a `test` block in `vite.config.js` to a new test-only `src/frontend/vitest.config.js` that merges `vite.config.js`. | The first run failed with `Cannot find module '/@fs/.../tests/unit/frontend/pages/Billing.test.jsx'`: Vite only loads files inside its workspace root (`src/frontend`). Allowing `tests/unit/frontend` in `vite.config.js` would also widen what the dev server can serve, so the allow-list and the other test-only settings live in a file only Vitest reads. The runner configuration still lives in `src/frontend/`, as architecture.md Section 3 requires. |
| R2 | 1 | `src/frontend/package-lock.json` rebuilt in a scratch folder so it records every platform's optional native binaries (rolldown, lightningcss, oxlint), with every existing entry's version, resolved URL and integrity unchanged (0 changed, 0 removed, 43 optional entries added, all from registry.npmjs.org). `npm audit` re-run on the final lock and saved again to `npm-audit-install.json` (same result). | The lock written by `npm install` next to the existing `node_modules` listed only the Windows binaries (a known npm behaviour), so `npm ci` on Linux, in the behaviour image or on any other machine, would install no native Vite binary. A committed lock must work on every platform (REQ-NF-06). |
| R3 | 9 | Two supporting files added to the behaviour runner bootstrap: `tests/.evals/behavior/resolve-tier.cjs` (resolves B1, B2 and B3 membership from `spec/behavior/` and the resolved Story Tracker, called by `run.sh`) and a root `.containerignore` (keeps `node_modules`, the backend venv, `.git` and `reports/` out of the image build context). | The tier rules need a small parser for the Story Tracker tables, which is clearer in Node than in shell; without the ignore file every build would upload about 170 MB of context. |

## Trace summary (REQ/AC to plan steps)

| REQ / AC | Plan steps |
|----------|------------|
| REQ-NF-05 | 1, 3, 4, 6, 7, 8, 9 |
| REQ-NF-06 | 1, 2, 5, 9 |
| AC-1 | 1, 9 |
| AC-2 | 3, 4, 6, 7, 8, 9 |
| AC-3 | 3, 4, 7, 8, 9 |
| AC-4 | 1, 2, 5, 9 |

Trace completeness self-check: both covered REQ-IDs and all 4 ACs map to at least one step. PASS.
