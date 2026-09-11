# API & Contract Testing Gate — Story 1.1

Endpoints: `GET /api/billing/upgrade-preview`, `POST /api/billing/upgrade`.
Test file: `tests/unit/backend/test_billing_upgrade.py` (FastAPI `TestClient`, same run as the unit
test/coverage gate — `unit-test-run-backend.log`).

| Checklist item | GET /upgrade-preview | POST /upgrade |
|---|---|---|
| Functional / happy path | `test_upgrade_preview_returns_documented_contract` | `test_confirm_upgrade_success_flips_plan_and_charges`, `test_confirm_upgrade_applies_premium_quotas` |
| Response-code validation | 200 (happy), 401 (unknown email), 409 (already-Premium) | 200, 401, 402 (declined), 409 (already-Premium) |
| Role-based authorization (401/403) | N/A — this codebase has no role concept anywhere (verified via `atlas-deep-dive.md`); the existing pattern is email-existence only (`if email not in users -> 401`), applied identically here, consistently with every other endpoint | N/A (same reason) |
| Error-response validation (format + code) | `{"detail": "already_premium"}` (409) — matches the documented shape | `{"detail": "card_declined", "message": "..."}` (402), `{"detail": "already_premium"}` (409) — both match the documented shape |
| Request validation (required fields/types) | `email` required (Pydantic query param — FastAPI 422 on missing, not separately re-tested here as it is framework-enforced, identical to every other `email: str` query param already in this codebase) | `UpgradeRequest.email: str` required — same FastAPI-enforced validation as `LoginRequest`/`RegisterRequest` |
| Response contract / schema validation | `test_upgrade_preview_returns_documented_contract` asserts all 6 documented keys present with correct types/values | `test_confirm_upgrade_success_flips_plan_and_charges` asserts the exact `{"status", "plan", "charge"}` shape |

**Gate verdict**: SH-LOOP-2 **PASS** on attempt 0 — every applicable checklist item passes; the two
N/A items are a genuine stack/app-wide inapplicability (no role model exists anywhere in this
codebase), not an unmeasured gap.
