# Evidence Manifest — Static Eval Gate D1–D7 — story-1.1

| Field | Value |
|---|---|
| Work unit | Story 1.1 — Upgrade to Premium on the Billing page (frontend only) |
| Branch / head | story/1.1-upgrade-to-premium-on-the-billing-page @ e6aa80b (+ uncommitted story changes) · base e6aa80b |
| Generated | 2026-10-23T15:31:51Z |
| AIRE version | 1.0 |
| Status | PASS |

## Commands run
| # | Command | Working directory | Exit code |
|---|---|---|---|
| 1 | `npx oxlint --format json src` (baseline) / `src/frontend/node_modules/.bin/oxlint -c src/frontend/.oxlintrc.json --format json src/frontend/src src/frontend/vitest*.js tests/unit tests/behavior` (post) | src/frontend / repo root | 0 / 0 |
| 2 | `semgrep --config p/javascript --config p/react --json --metrics off` over src/frontend/src (baseline) + tests/unit, tests/behavior, src/frontend/vitest*.js (post) | repo root | 0 / 0 |
| 3 | `npm audit --json` | src/frontend | 1 / 1 (findings present) |
| 4 | `npx license-checker-rseidelsohn@4.4.2 --json --start .` | src/frontend | 0 / 0 |
| 5 | `npx eslint@9.39.5 --no-config-lookup -c tests/.evals/eslint-complexity.config.mjs -f json` same file sets as D1 | src/frontend / repo root | 0 / 0 |
| 6 | `gitleaks dir src/frontend/src` (baseline) / `gitleaks dir <copy of every changed path>` (post) `--config tests/.evals/gitleaks.toml` | repo root | 0 / 0 |

## Tools
| Tool | Version |
|---|---|
| oxlint | 1.85.0 |
| semgrep | 1.127.0 |
| npm (audit) | 10.9.2 |
| license-checker-rseidelsohn | 4.4.2 (5.0.1 rejected: needs node ≥ 24) |
| eslint | 9.39.5 (complexity rule only) |
| gitleaks | 8.21.2 |

## Result
| D-gate | Tool | Baseline findings | Post-change findings | NEW on changed files | Threshold | Status |
|---|---|---|---|---|---|---|
| D1 Lint | oxlint | 3 warnings (AuthContext.jsx) | 3 (same) | 0 | ≤ 0 delta | PASS |
| D2 Types | — | — | — | — | 0 | N/A — plain JavaScript/JSX root, no type checker applies |
| D3 SAST | semgrep | 0 | 0 | 0 | 0C / 0H / ≤5M | PASS |
| D4 Deps | npm audit | 2 high (vite, source-map-js) | 2 high (same) + 4 moderate | 0C / 0H (4 moderate: uuid GHSA-w5hq-g745-h8pq chain, dev-only) | 0C / 0H | PASS |
| D5 Licences | license-checker | 0 disallowed / 29 pkgs | 0 disallowed / 144 pkgs | 0 | none of GPL-2.0, GPL-3.0, AGPL-3.0, SSPL-1.0 | PASS |
| D6 Complexity | eslint complexity | 0 | 0 (12 files) | 0 | ≤ 12 | PASS |
| D7 Secrets | gitleaks | 0 | 0 | 0 | 0 | PASS |

## Artifacts
| File | What it is |
|---|---|
| `oxlint.json`, `semgrep.json`, `npm-audit.json`, `license-report.json`, `eslint-complexity.json`, `gitleaks.json` | post-change raw tool output |
| `baseline/*` | the same tool set before any code change |
| `*.stderr.log` | tool stderr (warnings only) |

## Exceptions and notes
- The first post-change D1/D6 invocation passed `../../tests/*` paths from `src/frontend`; oxlint and ESLint both refuse paths outside the working directory (invocation error, no output). They were re-run from the repo root over the same file set. A semgrep invocation also stalled once and was stopped and re-run (completed in ~10 s, 0 findings). These were tool-invocation corrections, not remediation of findings (SH-LOOP-4: 0 attempts).
- D7 post-change scanned a copy of exactly the changed paths, so that `node_modules/` and `venv/` were excluded.
