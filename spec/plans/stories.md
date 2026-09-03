EPIC TICKET: EPIC-LOCAL-1 — Mid-Cycle Subscription Upgrade (Standard → Premium) (local Epic sourced from Helix solution document_id 3157 — see spec/plans/epic-brief.md; no external tracker URL, Type: LOCAL)

---

> **Note on granularity**: This story set is intentionally a **single story** covering the whole Epic, per an explicit user override during the Story Count question (see `runtime-artifacts/audit.md` — "User Stories — Story Count Question & Override"). The AIRE framework computed and recommended a 9-story SPIDR-sliced breakdown (frontend/backend split per interface, happy/declined paths split, guard clause isolated) that would keep every story within the Step 1.5 hard sizing ceilings (<=5 ACs, one architectural layer, one scenario class) and support team_size=2 parallel development. The user was shown that trade-off explicitly and confirmed proceeding with exactly 1 story anyway. **This story deliberately exceeds the Step 1.5 ceilings** (more than 5 ACs, two new architectural layers — backend + frontend, and three scenario classes — happy path / declined path / already-premium guard) as a knowing, logged exception, not an oversight.

---

## Story 1 — Mid-Cycle Subscription Upgrade (Standard → Premium)

**As a Standard subscriber, I want a self-serve way to upgrade to Premium mid-cycle — seeing the exact prorated charge before I commit, and a working (dummy) payment step — so that I can move to a higher tier without leaving the app or contacting support, while a Premium subscriber never sees a redundant upgrade option.**

**Persona**: Standard Subscriber ("Priya") for the upgrade path; Premium Subscriber for the guard behavior. See `personas.md`.

**Covers**: REQ-F-01, REQ-F-02, REQ-F-03, REQ-F-04, REQ-F-05, REQ-F-06, REQ-F-07, REQ-F-08, REQ-F-09, REQ-F-10, REQ-F-11, REQ-F-12, REQ-F-13, REQ-F-14, REQ-F-15, REQ-F-16, REQ-F-17, REQ-F-18, REQ-NF-01, REQ-NF-02, REQ-NF-03, REQ-NF-04, REQ-NF-05

**Requires**: none (only story in this set)
**Tracker ID**: LOCAL

### Acceptance Criteria (AC-n → REQ-ID)

**A. CTA & dynamic plan display**
- **AC-1** → REQ-F-01, REQ-F-02, REQ-F-03: The Billing page shows an "Upgrade to Premium" button only when `billing_data[email]["plan_name"] == "Standard"`; the plan badge, "Active" badge, and price are driven dynamically by the `GET /api/billing` response (the hardcoded `<span className="standard-badge">Standard</span>` at `Billing.jsx` line 128 is removed).

**B. Proration preview**
- **AC-2** → REQ-F-04, REQ-F-05, REQ-F-06, REQ-F-07, REQ-NF-01: Clicking the CTA opens a confirmation modal (no navigation) that calls `GET /api/billing/upgrade-preview?email=<email>` and renders `current_plan`, `new_plan`, `days_remaining`, `prorated_charge`, `next_renewal_price`, and `renew_at` exactly as returned — no client-side computation. The modal has "Confirm Upgrade" and "Cancel" actions; Cancel closes it with zero side effects.
- **AC-3** → REQ-F-08: The backend computes `days_remaining = max(1, (renew_at_date - today).days)` (parsing `renew_at` via `datetime.strptime(renew_at, "%b %d, %Y")`), `daily_delta = (40.0 - 20.0) / 30`, `prorated_charge = round(daily_delta * days_remaining, 2)`.

**C. Dummy payment gateway**
- **AC-4** → REQ-F-09, REQ-NF-02, REQ-NF-03: A new `charge_card(email: str, amount: float) -> dict` function returns `{"status": "card_declined", "message": "Your card was declined."}` when `email.startswith("fail")`, else `{"status": "success"}` — deterministic, no external service, no new dependency.

**D. Execute upgrade — happy path**
- **AC-5** → REQ-F-10, REQ-F-11, REQ-F-14, REQ-F-15, REQ-F-17: On "Confirm Upgrade", `POST /api/billing/upgrade {"email": ...}` calls `charge_card`; on `success` it sets `users[email]["plan"]="Premium"` / `["price"]="$40/month"`, sets `billing_data[email]["plan_name"]="Premium"` / `["price"]="$40/month"`, updates `usages` to Premium quotas (chat credits 10000, chatbots 10, document pages 5000, each `used` reset to 0), updates `on_demand_usage.notice` to `"On-demand credit is available on your Premium plan."`, leaves `renew_at` unchanged, and returns HTTP 200 `{"status": "success", "plan": "Premium", "charge": <prorated_charge>}`.
- **AC-6** → REQ-F-12: On a successful response, the frontend re-fetches `GET /api/billing`, closes the modal, hides the CTA, and shows the banner `"You're now on Premium! $<charge>.00 was charged."`.

**E. Execute upgrade — declined path**
- **AC-7** → REQ-F-13, REQ-NF-04: When `charge_card` returns `card_declined`, the backend makes **no** mutation to `users` or `billing_data` and returns **HTTP 402** `{"detail": "card_declined", "message": "Your card was declined."}` (FastAPI `HTTPException`, consistent with existing error conventions); the frontend shows `"Payment failed: Your card was declined. Your plan has not changed."` inline in the modal, which stays open.

**F. Already-Premium guard**
- **AC-8** → REQ-F-16: Both `GET /api/billing/upgrade-preview` and `POST /api/billing/upgrade` return **HTTP 409** `{"detail": "already_premium"}` and mutate nothing when `billing_data[email]["plan_name"] == "Premium"`; the frontend never renders the CTA for a Premium user (covered by AC-1's condition).

**G. Scope guardrails**
- **AC-9** → REQ-F-18, REQ-NF-05: No changes are made to `/api/auth/login`, `/api/auth/register`, `/api/users/me`, `/api/tasks` (GET/POST), or `AuthContext.jsx`'s token pattern. The in-memory nature of the store (reset on server restart) is accepted POC behavior, not a defect to fix here.

### Files Touched
- `backend/main.py` — `PLANS`, `PREMIUM_QUOTAS`, `DAYS_IN_CYCLE` constants; `UpgradeRequest` Pydantic model; `charge_card()`; `GET /api/billing/upgrade-preview`; `POST /api/billing/upgrade`
- `frontend/src/pages/Billing.jsx` — dynamic plan badge/price, conditional CTA, upgrade modal state, `fetchUpgradePreview()`, `confirmUpgrade()`, success banner / inline error handling

### Out of Scope (unchanged from Epic)
Downgrades, refunds/credits, Enterprise tier, real payment provider integration, email receipts/notifications.

---

## Requirements Coverage Matrix

| REQ-ID | Covering Story | Status |
|---|---|---|
| REQ-F-01 | Story 1 (AC-1) | Covered |
| REQ-F-02 | Story 1 (AC-1) | Covered |
| REQ-F-03 | Story 1 (AC-1) | Covered |
| REQ-F-04 | Story 1 (AC-2) | Covered |
| REQ-F-05 | Story 1 (AC-2) | Covered |
| REQ-F-06 | Story 1 (AC-2) | Covered |
| REQ-F-07 | Story 1 (AC-2) | Covered |
| REQ-F-08 | Story 1 (AC-3) | Covered |
| REQ-F-09 | Story 1 (AC-4) | Covered |
| REQ-F-10 | Story 1 (AC-5, AC-6) | Covered |
| REQ-F-11 | Story 1 (AC-5) | Covered |
| REQ-F-12 | Story 1 (AC-6) | Covered |
| REQ-F-13 | Story 1 (AC-7) | Covered |
| REQ-F-14 | Story 1 (AC-5) | Covered |
| REQ-F-15 | Story 1 (AC-5) | Covered |
| REQ-F-16 | Story 1 (AC-8) | Covered |
| REQ-F-17 | Story 1 (AC-5) | Covered |
| REQ-F-18 | Story 1 (AC-9) | Covered |
| REQ-NF-01 | Story 1 (AC-2) | Covered |
| REQ-NF-02 | Story 1 (AC-4) | Covered |
| REQ-NF-03 | Story 1 (AC-4) | Covered |
| REQ-NF-04 | Story 1 (AC-7) | Covered |
| REQ-NF-05 | Story 1 (AC-9) | Covered |

**Coverage**: 23/23 REQ-IDs fully covered by Story 1's acceptance criteria. (Single-story shape per user override — see the granularity note above; Step 18.6's automatic ceiling-violation splitting was deliberately not applied, per the user's explicit, disclosed confirmation logged in `runtime-artifacts/audit.md`.)
