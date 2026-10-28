### Eval Scorecard — Story 1.1 · **PASS**

| Gate | Result | Threshold | Status |
|---|---|---|---|
| D1 Lint | 0 new findings (3 pre-existing in AuthContext.jsx) | ≤ 0 delta | PASS |
| D2 Type check | the frontend is plain JavaScript (.jsx sources, no tsconfig or jsconfig, no TypeScript); no type checker applies to this stack (eval-framework.md Section 2.5.1 reason 1) | 0 | N/A |
| D3 Static security | 0C / 0H / 0M new | 0C / 0H / ≤5M | PASS |
| D4 Dependencies | 0C / 0H new (2 high pre-existing: vite 8.3.0, source-map-js) | 0C / 0H | PASS |
| D5 Licences | 0 violations (113 packages) | none disallowed | PASS |
| D6 Complexity | 0 functions over the limit | ≤ 12 | PASS |
| D7 Secrets | 0 findings | 0 | PASS |
| Unit coverage | 100.0% of changed lines (0 changed executable lines) · 4/4 tests | ≥ 90.0% | PASS |
| Behavioural B1 (this story) | 5/5 scenarios · 4/4 ACs · podman | 100% | PASS |
| Behavioural B2 (cumulative) | no other active feature file: story-1.2 to story-1.6 are Ready for Development and excluded by the activation rule (behavior-spec.md Section 6.0); the repo holds no feature file from an earlier cycle | 100% | N/A |
| Behavioural B3 (epic scope) | not the last work unit: 1.2, 1.3, 1.4, 1.5 and 1.6 have no merged PR (gh pr list against the epic branch returned no PRs) | last unit only | N/A |
| API & contract | the plan has no API Layer Generation step; Story 1.1 adds test tooling and no endpoint | all applicable | N/A |
| Regression | 0 new failures (baseline had no tests; now 4 pass) | 0 | PASS |
| J1 Architecture | 1.00 | ≥ 0.85 | PASS |
| J2 Security (OWASP 2025) | 1.00 | ≥ 0.85 | PASS |

**J1 breakdown** (rubric v1.0.0):
- ARCH-01 (weight 0.25): 1.0 — No file under src/backend/ changes. The only file added under src/frontend/ with code is vitest.config.js (test configuration: file-system allow-list, dedupe, jsdom, coverage); it adds no fetch, XMLHttpRequest, axios or request URL. package.json adds scripts and devDependencies only.
- ARCH-02 (weight 0.2): N/A — The diff adds no Premium value, no plan constant and no plan-card, usage-card or perks markup (no application source under src/frontend/src changes); this criterion is exercised from Story 1.4 onward.
- ARCH-03 (weight 0.2): N/A — The diff adds no plan or upgrade state anywhere (no application source changes); nothing is stored, globalised or sent.
- ARCH-04 (weight 0.15): 1.0 — None of dangerouslySetInnerHTML, innerHTML, outerHTML or insertAdjacentHTML appears in any file the diff adds or changes under src/frontend/ (package.json, package-lock.json, vitest.config.js, .gitignore, README.md).
- ARCH-05 (weight 0.1): N/A — Billing.jsx is unchanged; the diff changes no fetch chain (Story 1.3 changes it).
- ARCH-06 (weight 0.1): 1.0 — vitest, @vitest/coverage-v8, jsdom, @testing-library/react and @testing-library/dom are added under devDependencies (src/frontend/package.json:20-29); dependencies (lines 14-18) are unchanged; src/frontend/package-lock.json is added in the same diff with every new entry resolved from registry.npmjs.org, sha512 integrity, dev true (package-lock.json:958, 978, 1088, 1442, 2302).

**J2 breakdown** (rubric v1.0.0):
- SEC-01 · A01:2025 (weight 0.1): N/A — The diff changes no route, page guard or API handler.
- SEC-02 · A02:2025 (weight 0.05): 1.0 — Changed configuration: package.json adds test scripts only (src/frontend/package.json:11-12); vite.config.js is unchanged, so the dev server, its /api proxy and the production build are untouched. The widened server.fs.allow (src/frontend/vitest.config.js:15) applies only to Vitest's own in-process server during test runs, which listens on no port. Test tooling is devDependencies only and is not part of the production build. No CORS, debug mode or source-map change.
- SEC-03 · A03:2025 (weight 0.15): 1.0 — The lock gains 127 entries over the baseline tree, 84 packages (the 5 direct dev dependencies and their transitive packages) plus 43 optional platform binaries of rolldown, lightningcss and oxlint, and all 155 lock entries resolve from https://registry.npmjs.org/ with sha512 integrity; the lock file is committed in the same diff; no test library is in dependencies; the npm audit evidence (reports/eval-evidence/story-1.1/npm-audit-install.json) reports no high or critical advisory reaching an added package. The two high advisories it lists (vite 8.3.0, source-map-js 1.2.1) are on packages that existed before this diff.
- SEC-04 · A05:2025 (weight 0.2): N/A — The diff changes no rendering path or request path in application code (no file under src/frontend/src changes); the test file renders the unchanged Billing page against a stub.
- SEC-05 · A06:2025 (weight 0.15): N/A — The diff contains no business-logic change, no plan change and no server call.
- SEC-06 · A07:2025 (weight 0.1): N/A — The diff changes no authentication or session handling; the unit test mocks useAuth with the demo account email and stores nothing.
- SEC-07 · A09:2025 (weight 0.1): 1.0 — The only new output statements are in tests/.evals/behavior/run.sh (lines printing the tier, unit key, tool versions and feature-file names) and the test runners' own reports; none prints a token, password, email from user data or an API response body. No console.log or console.error is added.
- SEC-08 · A10:2025 (weight 0.15): N/A — The diff adds no fetch or async external call in application code; Billing.jsx's existing fetch is unchanged (Story 1.3 changes it).

**Verdict**: PASS · judge `claude-opus-5-5` · rubric v1.0.0 (from `architecture.md` v1.0.0)
**Self-healing**: all loops 0/3
**Static Eval**: 6 of 7 checks ran — D2 N/A (plain JavaScript, no type checker applies)
**Bootstrapped**: tests/.evals/oxlint-complexity.json (D6), .gitleaks.toml (D7), behaviour runner (tests/.evals/behavior/, .containerignore)
