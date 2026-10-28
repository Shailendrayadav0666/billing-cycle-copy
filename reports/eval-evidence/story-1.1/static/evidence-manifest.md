# Evidence Manifest — Static Eval D1-D7 — story-1.1

| Field | Value |
|---|---|
| Work unit | Story 1.1 — Frontend unit-test tooling |
| Branch / head | story/1.1-frontend-unit-test-tooling @ 6c0f1a5 (working tree, story changes staged) · base 6c0f1a5 |
| Generated | 2026-10-28T10:31:38Z |
| AIRE version | 1.0 |
| Status | PASS |

## Commands run
| # | Command | Working directory | Exit code |
|---|---|---|---|
| 1 | D1 `npx oxlint --format json .` (baseline and post-change) | src/frontend | 0 |
| 2 | D1 `src/frontend/node_modules/.bin/oxlint -c src/frontend/.oxlintrc.json --format json tests/unit/frontend tests/behavior tests/.evals/behavior` (post-change; oxlint rejects ".." paths, so the new test code is linted from the repo root with the same config) | repository root | 0 |
| 3 | D6 `npx oxlint -c ../../tests/.evals/oxlint-complexity.json --format json src` (baseline and post-change) | src/frontend | 0 |
| 4 | D6 `oxlint -c tests/.evals/oxlint-complexity.json --format json tests/unit/frontend tests/behavior tests/.evals/behavior` (post-change) | repository root | 0 |
| 5 | D4 `npm audit --json` | src/frontend | 1 (exit 1 = advisories present; all pre-existing) |
| 6 | D5 `npx --yes license-checker@25.0.1 --json` | src/frontend | 0 |
| 7 | D3 `semgrep scan --config auto --metrics on --json --quiet <paths>` (baseline: src/frontend; post-change: src/frontend tests/unit tests/behavior tests/.evals/behavior) | repository root | 0 |
| 8 | D7 baseline `gitleaks git --config .gitleaks.toml --report-format json .` (full history); post-change `gitleaks git --pre-commit --staged --config .gitleaks.toml --report-format json .` | repository root | 0 |
| 9 | diff: findings matched on (rule, file, message) with repo-root-relative paths, limited to files this unit changed (delta-summary.json) | repository root | 0 |

## Tools
| Tool | Version |
|---|---|
| oxlint | 1.85.0 (project devDependency) |
| semgrep | 1.127.0 |
| npm audit | npm 10.9.2 |
| license-checker | 25.0.1 (npx, so the measured tree is not altered) |
| gitleaks | 8.21.2 |

## Result
| Gate | Tool | Baseline findings | Post-change findings | NEW on changed files | Threshold | Status |
|---|---|---|---|---|---|---|
| D1 Lint | oxlint (.oxlintrc.json as-is) | 3 | 3 | 0 | lintErrorsAllowedDelta 0 | PASS |
| D2 Type check | — | — | — | — | typeErrorsAllowed 0 | N/A — plain JavaScript (.jsx, no tsconfig or jsconfig); no type checker applies (Section 2.5.1 reason 1) |
| D3 SAST | semgrep --config auto | 2 (WARNING, generated coverage/prettify.js) | 0 | 0 | 0C / 0H / 5M | PASS |
| D4 Dependencies | npm audit | 2 high (vite 8.3.0, source-map-js 1.2.1) | 2 high (same advisories) | 0 | 0C / 0H | PASS |
| D5 Licences | license-checker | 29 packages, 0 disallowed | 113 packages, 0 disallowed | 0 | disallowedLicenses | PASS |
| D6 Complexity | oxlint complexity, max 12 | 0 | 0 | 0 | maxCyclomaticComplexity 12 | PASS |
| D7 Secrets | gitleaks | 0 | 0 | 0 | secretFindingsAllowed 0 | PASS |

Static Eval: PASS (6 of 7 checks ran — D2 N/A, see reason).

## Artifacts
| File | What it is |
|---|---|
| oxlint.json · oxlint-tests.json | D1 post-change output (src/frontend; test and behaviour code) |
| complexity.json · complexity-tests.json | D6 post-change output |
| semgrep.json | D3 post-change output |
| npm-audit.json | D4 post-change output |
| license-report.json | D5 post-change output |
| gitleaks.json | D7 post-change output (staged diff) |
| delta-summary.json | per-gate baseline vs post-change comparison and NEW findings |
| static-run.log | every command, exit code and tool version |
| baseline/ | the same tools before any change (oxlint, complexity, semgrep, npm-audit, license-report, gitleaks) |

## Exceptions and notes
- The D3 baseline findings came from the untracked generated folder src/frontend/coverage/; this unit adds `coverage` to src/frontend/.gitignore, so semgrep no longer scans it.
- D4: the two high advisories (vite 8.3.0 via launch-editor, GHSA-587h-7wmj-h5pm and related; source-map-js 1.2.1, GHSA-68fv-2mgg-jv7q) were present before this unit and reach no newly added package. They are pre-existing debt, not fixed here; fix versions exist (vite 8.3.5). Recommend a defect via `/raise-defect`.
- D6 was proven live: a probe function with complexity 13 is reported by the same config ("complexity of 13. Maximum allowed is 12").
- Self-healing: SH-LOOP-4 used 0 attempts. The first post-change run produced empty D1/D6 output because oxlint rejects ".." paths; the run was split (commands 2 and 4) and re-run before any diff, so this is a measurement fix, not a gate attempt.
