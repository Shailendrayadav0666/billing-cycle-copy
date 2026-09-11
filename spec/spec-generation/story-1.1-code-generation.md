# Code Generation Plan — Story 1.1 (Mid-Cycle Subscription Upgrade)

**Context**: single-story epic cycle. Grounded in `spec/plans/stories.md` (Story 1.1, ACs 1-9),
`spec/plans/requirements.md` (REQ-F-01..13, REQ-NF-01..04), and `spec/plans/architecture.md`
(ARCH-01..05). No API Layer step is skipped — this story adds two new endpoints, so the API &
Contract Testing Gate (Step 6.2) applies.

## Steps

- [x] 1. **Backend constants + model** (`src/backend/main.py`) — add `PLANS`, `PREMIUM_QUOTAS`,
      `DAYS_IN_CYCLE`, `UpgradeRequest` Pydantic model. — REQ-F-04, REQ-F-10 / AC4, AC6
- [x] 2. **`charge_card(email, amount)`** — pure deterministic dummy gateway. — REQ-F-07, REQ-NF-01 / AC5
- [x] 3. **`GET /api/billing/upgrade-preview`** — already-Premium guard (ARCH-04) first, then proration
      (`days_remaining = max(1, ...)`, `daily_delta`, `prorated_charge`) per ARCH-01/REQ-F-04. — REQ-F-03,
      REQ-F-04, REQ-F-11 / AC4, AC8
- [x] 4. **`POST /api/billing/upgrade`** — already-Premium guard first (ARCH-04); recompute proration
      server-side (never trust a client-sent amount, ARCH-01); call `charge_card`; on `card_declined`
      return 402 with NO mutation (ARCH-03) and never touch `renew_at` (ARCH-05); on success mutate
      `users`/`billing_data` to Premium + apply `PREMIUM_QUOTAS` + update `on_demand_usage.notice`. —
      REQ-F-05, REQ-F-06, REQ-F-08, REQ-F-09, REQ-F-10, REQ-F-11, REQ-F-13, REQ-NF-02 / AC5, AC6, AC7, AC8, AC9
- [x] 5. **Frontend: dynamic plan badge** (`Billing.jsx`) — replace the hardcoded `"Standard"` span
      with `data.plan_name`. — REQ-F-02 / AC2
- [x] 6. **Frontend: conditional CTA** — "Upgrade to Premium" button when `data.plan_name === "Standard"`.
      — REQ-F-01, REQ-F-11 / AC1, AC8
- [x] 7. **Frontend: confirmation modal** — fetch `GET /api/billing/upgrade-preview` on CTA click, render
      the returned values only (never recompute, REQ-NF-03/ARCH-01), Confirm/Cancel actions. — REQ-F-05 / AC3
- [x] 8. **Frontend: confirm handler** — call `POST /api/billing/upgrade`; on success re-fetch
      `GET /api/billing`, show success banner, close modal; on 402 show inline error, keep modal open,
      no data change; on 409 hide the CTA (already-Premium). — REQ-F-06, REQ-F-08, REQ-F-09, REQ-F-12 /
      AC6, AC7
- [x] 9. **Unit tests + coverage gate** — `tests/unit/backend/test_billing_upgrade.py` (pytest, FastAPI
      TestClient), `tests/unit/frontend/Billing.test.jsx` (vitest + Testing Library), to
      `unitTestCoverageMin` on changed code.
- [x] 10. **API & Contract Testing Gate** — functional/happy path, response codes, error-response shape,
      request validation, response contract for both new endpoints (no auth/role model beyond the
      existing email-as-token pattern — REQ-NF-02 keeps that unchanged).
- [x] 11. **Behaviour spec** — `spec/behavior/story-1.1.feature`, one scenario per AC.

## REQ/AC Trace Completeness Self-Check

- REQ-F-01..13: covered by steps 3, 4, 6 (and 1/2 as their supporting constants/gateway).
- REQ-NF-01..04: REQ-NF-01 (step 2), REQ-NF-02 (steps 4, unchanged auth), REQ-NF-03 (steps 4/7), REQ-NF-04 (no downgrade/refund/enterprise/email code added anywhere in this plan).
- AC1-AC9 (stories.md Story 1.1): AC1→6, AC2→5, AC3→7, AC4→1/3, AC5→2/7, AC6→4/8, AC7→4/8, AC8→3/4/6, AC9→4 (no auth files touched).
- Every REQ-ID and every AC appears in >=1 step. PASS.
