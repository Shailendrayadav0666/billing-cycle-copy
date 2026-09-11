# Static Eval Baseline — Story 1.1 (captured before any code change)

| Gate | Tool | Result | Pre-existing findings |
|---|---|---|---|
| D1 Lint (backend) | ruff 0.8.4 (`ruff.toml` created — recommended preset + `C901` at maxCyclomaticComplexity=12) | PASS | 0 |
| D1 Lint (frontend) | oxlint (existing `.oxlintrc.json`, used as-is) | 4 findings | `Tasks.jsx` exhaustive-deps; `AuthContext.jsx` immutability, only-export-components, exhaustive-deps — all pre-existing, none touching `Billing.jsx` |
| D2 Type check | mypy 1.14.1 (created `mypy` run with `--ignore-missing-imports`, default strictness) | 2 errors | `main.py:203` — `max()` type-var/operator errors in the existing `add_task` endpoint — pre-existing, unrelated to billing |
| D3 SAST | semgrep 1.127.0 `--config auto` | 1 WARNING | `python.fastapi.security.wildcard-cors` at `main.py:12` — existing `allow_origins=["*"]`, explicitly out of scope (architecture.md Section 6) |
| D4 Deps (backend) | pip-audit 2.9.0 | 0 vulns | none |
| D4 Deps (frontend) | `npm audit --json` | 6 vulns (3 moderate, 1 high, 2 critical) | pre-existing transitive deps — see `npm-audit-baseline.json`; not introduced by this story |
| D5 Licenses (backend) | pip-licenses | 0 flagged | none against `disallowedLicenses` |
| D5 Licenses (frontend) | `license-checker` (206 packages) | 0 flagged | none |
| D6 Complexity | ruff `C901` (backend); no complexity rule available for oxlint — recorded, not fabricated | 0 over threshold | n/a |
| D7 Secrets | gitleaks 8.21.2 (binary installed — Podman OCI pull unavailable, see aire-state.md Environment Notes) | 0 leaks | none |

**Bootstrap performed** (recorded per `common/eval-framework.md` Section 2.3): created `src/backend/ruff.toml` (D1+D6), installed `mypy`, `semgrep`, `pip-audit`, `pip-licenses`, `gitleaks` (Windows binary, github.com release — not the Podman OCI rung, which is network-blocked in this environment per `aire-state.md`).

**Rule applied**: every finding above is pre-existing debt on the epic branch (introduced before this story). None of it is fixed or blocked on by Story 1.1 — it exists only to let the post-implementation Static Eval Gate (Step 6.6) tell this story's own findings apart from everyone else's.
