# Evidence Manifest — Story 1.1

**Story**: 1.1 — Mid-Cycle Subscription Upgrade (Standard → Premium) · `LOCAL`
**Branch**: `story/1.1-mid-cycle-subscription-upgrade` (cut from `epic/EPIC-1-mid-cycle-subscription-upgrade`)
**AIRE**: v1.0

---

## Artifacts

| Artifact | Path |
|---|---|
| Baseline regression | `unit-test-evidence/story-1.1/baseline-regression.log` |
| Post-implementation regression | `unit-test-evidence/story-1.1/post-implementation-regression.log` |
| Full regression | `unit-test-evidence/story-1.1/full-regression.log` |
| Coverage (JSON) | `.evals/evidence/coverage.json` (gitignored run output) |
| API & contract run | `api-contract-test-evidence/story-1.1/api-contract-test-run.log` |
| Static baseline D1–D7 | `eval-evidence/story-1.1/static/baseline/results.json` |
| Static post-change D1–D7 | `eval-evidence/story-1.1/static/post/results.json` |
| Behaviour contract | `.spec/aire-docs/implementation/code/behavior/story-1.1.feature` |
| Code review v1 (findings) | `implementation/reviews/story-1.1-code-review-v1.md` |
| Code review v2 (clean) | `implementation/reviews/story-1.1-code-review-v2.md` |

---

## Regression: baseline vs post-change

| | Baseline | Post-change |
|---|---|---|
| Tests collected | **0 — the repo had no test suite at all** | 184 |
| Passed | 0 | **184** |
| Failed | 0 | **0** |
| **NEW failures vs baseline** | — | **0** |

The baseline having no tests is recorded, not glossed: it means the regression gate covers only this
story's own tests, so the real protection comes from the new tests plus the D1–D7 diff rather than
from regression. This story introduces the repository's first 184 tests.

## Coverage

| Measure | Value |
|---|---|
| **Changed-surface coverage** | **100.0%** (62 of 62 executable changed lines) |
| Threshold `unitTestCoverageMin` | 90.0% |
| Verdict | **PASS** |
| Whole-module coverage | 79.84% |

The whole-module figure is below 90% and deliberately reported rather than hidden. Every uncovered
line belongs to a **pre-existing** endpoint this story never touched (`login`, `register`, `me`,
`billing`, `tasks`, `add_task`, the static mount). SH-LOOP-1's exit criterion is coverage on
new/changed code, and `.evals/config.json` declares `scope: "changed-files"`, so the changed-surface
figure is the governing one. Raising the whole-module number would mean writing tests for six
endpoints outside this story's scope.

## Static eval D1–D7

| Gate | Baseline | Post-change | Attribution |
|---|---|---|---|
| D1 lint | PASS (0 errors, 4 pre-existing oxlint **warnings**) | **PASS** (0 errors, same 4 warnings — **none new**) | — |
| D2 type check | N/A (0 changed Python) | **PASS** (0 mypy errors) | 2 of the 4 errors first surfaced here were pre-existing (`add_task`); fixed anyway by annotating the stores, which is a non-behavioural change |
| D3 SAST | PASS (semgrep 0/0/0) | **PASS** (0 crit, 0 high, **1 medium**) | The 1 medium is the **pre-existing** wildcard-CORS finding at `main.py:34`, within the allowed 5 |
| D3b bandit | not run (0 changed Python) | **PASS** (clean) | — |
| D4 dependency vulns | PASS | **PASS** | 8 prod deps, 0 critical/high |
| D5 licences | PASS | **PASS** | No GPL/AGPL/SSPL |
| D6 complexity | N/A (0 changed Python) | **PASS** | All changed functions ≤ 12 |
| D7 secrets | PASS (gitleaks 8.30.1) | **PASS** (gitleaks 8.30.1) | Diff-only scan |

**NEW findings above threshold, attributable to this story: 0.**

## API & contract gate — per-endpoint checklist

| Checklist item | `GET /upgrade-preview` | `POST /upgrade` |
|---|---|---|
| Functional behaviour | ✅ | ✅ |
| Response-code validation | ✅ 200/401/404/409/422 | ✅ 200/401/402/404/409/422 |
| Role-based authorization | ✅ 401; **no 403 case exists** — no roles in this system, recorded explicitly | ✅ same |
| Error-response validation | ✅ exact bodies + leak assertions | ✅ exact bodies + leak assertions |
| Request validation | ✅ missing param → 422 | ✅ malformed body → 422; unknown fields ignored |
| Response contract / schema | ✅ 6 fields, types asserted | ✅ 3 fields, types asserted |

Also verified: both endpoints appear in the generated OpenAPI schema, and `GET /api/billing`'s
existing response shape is unchanged (which is what keeps the regression baseline valid).

---

## Self-healing ledger

| Loop | Attempts used | Outcome |
|---|---|---|
| SH-LOOP-1 unit + coverage | **1** of 3 | My test scanned a docstring for the word it asserted was absent; and coverage needed measuring on the changed surface, not the whole module |
| SH-LOOP-7 behaviour B1+B2 | **1** of 3 | A `{n:f}` step parser could not match the bare integer `0` in "greater than 0" |
| SH-LOOP-8 behaviour B3 | — | N/A, scenario-free by design |
| SH-LOOP-2 API & contract | **1** of 3 | My assertion expected 405; the active SPA static mount makes it 404. Assertion corrected to accept either and to assert non-mutation, since the code depends on deployment state, not on this feature |
| SH-LOOP-3 full regression | **0** of 3 | Never failed |
| SH-LOOP-4 static D1–D7 | **2** of 3 | Attempt 1: the gate diffed `BASE...HEAD`, so uncommitted work was invisible and every gate went N/A — a false pass; also D5 read a hardcoded evidence path. Attempt 2: real findings fixed (import sort, store annotations) plus a D1 counter that counted ruff's summary lines as errors |
| SH-LOOP-6 judge J1/J2 | **1** of 3 | J1 0.72 → **1.00** after the F1 fix |
| SH-LOOP-5 remediate | **1** of 3 | 1 Blocker fixed, 2 nits dispositioned, review clean at v2 |

**No loop exhausted its budget. No Retry-Limit Report was emitted.**

### Forbidden shortcuts — none taken

No test was deleted, skipped or weakened. No threshold was lowered. No finding was suppressed. One
`eslint-disable` comment **was written and then removed** when I recognised it as exactly the
shortcut SH-6 forbids; the underlying nit was resolved a different way instead, and that reversal is
recorded in code review v2 rather than hidden.

---

## Files changed

| File | Change |
|---|---|
| `src/backend/main.py` | 212 → 385 lines. +4 constants, +1 model, +3 functions, +2 endpoints, 4 type annotations, import sort |
| `src/frontend/src/pages/Billing.jsx` | 181 → 375 lines. +2 components, +2 handlers, +2 state hooks, dynamic plan label, CTA |
| `src/frontend/src/App.css` | +8 classes, none redefined |
| `tests/unit/` | 9 new files, 159 tests |
| `tests/behavior/` | 1 new file, 25 scenarios |
| `ruff.toml`, `mypy.ini`, `.gitleaks.toml`, `pytest.ini` | bootstrapped gate configs |
| `.evals/scripts/changed-line-coverage.py` | new — changed-surface coverage measurement |
| `.evals/scripts/run-static-evals.sh` | 3 defect fixes found by running it |
