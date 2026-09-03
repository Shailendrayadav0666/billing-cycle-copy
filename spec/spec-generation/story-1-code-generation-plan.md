# Code Generation Plan — Story 1: Mid-Cycle Subscription Upgrade

**Grounded in**: `spec/plans/stories.md` (Story 1, AC-1..AC-9), `spec/plans/requirements.md` (REQ-F-01..18, REQ-NF-01..05), `spec/plans/epic-brief.md` (Technical Design Notes), `spec/plans/architecture.md` (Section 10 ARCH-01..05).

**Design References**: none registered in `## Design References` (user opted out of Context Project inputs) — nothing to re-ground here (DR-5 N/A).

## Steps

- [ ] **1. Backend — constants & model** (`src/backend/main.py`) — Covers REQ-F-08, REQ-F-09, REQ-F-14 / AC-3, AC-4, AC-5
  - Add `UpgradeRequest(BaseModel)` with `email: str`
  - Add `PLANS`, `PREMIUM_QUOTAS`, `DAYS_IN_CYCLE` constants exactly as specified in epic-brief.md Technical Design Notes

- [ ] **2. Backend — `charge_card()` pure function** — Covers REQ-F-09, REQ-NF-02, REQ-NF-03 / AC-4 / ARCH-02
  - `def charge_card(email: str, amount: float) -> dict`, no network call, no new dependency

- [ ] **3. Backend — `GET /api/billing/upgrade-preview`** — Covers REQ-F-04..F-08, REQ-F-16, REQ-NF-01 / AC-2, AC-3, AC-8 / ARCH-01, ARCH-04
  - Already-Premium guard (409) BEFORE any proration math
  - Server-side proration per the epic's exact formula (`datetime.strptime`, `max(1, ...)`, `round(..., 2)`)

- [ ] **4. Backend — `POST /api/billing/upgrade`** — Covers REQ-F-10, F-11, F-13, F-14, F-15, F-16, F-17, REQ-NF-04 / AC-5, AC-7, AC-8 / ARCH-02, ARCH-03, ARCH-04
  - Already-Premium guard (409) FIRST
  - Call `charge_card`; on `card_declined` → HTTPException(402), **zero mutation before this check**
  - On `success` → mutate `users[email]`, `billing_data[email]` (plan/price/usages/on_demand_usage.notice), `renew_at` untouched, return 200

- [ ] **5. Frontend — dynamic plan badge/price + CTA** (`src/frontend/src/pages/Billing.jsx`) — Covers REQ-F-01, F-02, F-03 / AC-1
  - Replace the hardcoded `"Standard"` span (line ~128) with `data.plan_name`
  - Conditional "Upgrade to Premium" button when `data.plan_name === "Standard"`

- [ ] **6. Frontend — confirmation modal** — Covers REQ-F-04, F-05, F-07, REQ-NF-01 / AC-2
  - `fetchUpgradePreview()` calling `GET /api/billing/upgrade-preview`; render only API values, no client math
  - Confirm/Cancel actions

- [ ] **7. Frontend — execute upgrade wiring** — Covers REQ-F-10, F-12, F-13 / AC-6, AC-7
  - `confirmUpgrade()` calling `POST /api/billing/upgrade`; success → re-fetch billing, banner, close modal; declined → inline error, modal stays open

- [ ] **8. Scope guardrail check** — Covers REQ-F-18, REQ-NF-05 / AC-9 / ARCH-05
  - No edits to `/api/auth/*`, `/api/users/me`, `/api/tasks`, or `AuthContext.jsx`

- [ ] **9. Unit Test & Coverage Gate** (Step 11a) — pytest unit tests for `charge_card`, the proration formula, both endpoints (success/declined/already-premium/guard paths) to ≥90% coverage on changed backend code

- [ ] **10. Behaviour spec** — `spec/behavior/story-1.feature`, one scenario per AC (AC-1..AC-9), tagged `@AC-n`

- [ ] **11. API & Contract Testing Gate** (applicable — 2 new endpoints) — functional, response-code, error-response, request validation, response schema for both endpoints

## REQ/AC Trace Completeness Check
Every REQ-ID from `requirements.md` (REQ-F-01..18, REQ-NF-01..05) and every AC (AC-1..AC-9) from `stories.md` appears in at least one step above. ✅ PASS.

## Announcement (auto-approved — no gate)
Plan finalized, 11 steps, grounded in the story's own ACs (already fully specified — no invented scope). Executing immediately.
