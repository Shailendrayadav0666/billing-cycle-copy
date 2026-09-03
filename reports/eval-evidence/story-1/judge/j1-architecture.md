# J1 — Architecture Conformance — Story 1

**Rubric**: `tests/.evals/rubrics/architecture-rubric.json` v1.0.0
**Judge model**: claude-sonnet-5

| ID | Criterion | Weight | Score | Citation |
|---|---|---|---|---|
| ARCH-01 | Server-side-only proration | 0.25 | 1.0 | `Billing.jsx` renders `preview.prorated_charge`/`days_remaining` verbatim from the API response; no arithmetic combining plan prices or `renew_at` appears in the frontend diff |
| ARCH-02 | Deterministic gateway, no external call | 0.20 | 1.0 | `main.py` `charge_card()` — no `requests`/`httpx`/`urllib` import, no new pip dependency, no `os.environ` read |
| ARCH-03 | Declined payment mutates nothing | 0.20 | 1.0 | `main.py` `upgrade()` — `users[email]`/`account` mutations appear only after `charge_result["status"] != "success"` returns early via `JSONResponse` |
| ARCH-04 | Already-Premium guard on both endpoints | 0.20 | 1.0 | Both `upgrade_preview()` and `upgrade()` check `account["plan_name"] == "Premium"` and raise 409 before any proration/mutation logic |
| ARCH-05 | No scope creep into unrelated endpoints | 0.15 | 1.0 | `git diff` confirms zero hunks inside `/api/auth/*`, `/api/users/me`, `/api/tasks`, or `AuthContext.jsx` |

**J1 = 1.00** (weights sum 1.0) — **PASS** (≥ `llmJudgeArchitectureScoreMin` 0.85 from `tests/.evals/config.json`)
