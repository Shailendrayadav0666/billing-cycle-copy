# Stories — Mid-Cycle Subscription Upgrade (Standard → Premium)

**Single-story cycle** (user-requested consolidation of the original 5-story split): the whole Epic
ships as one story, one branch, one PR — the Epic is small and fully specified end-to-end, so splitting
it added coordination overhead without enabling real parallelism.

## Story 1.1 — Mid-Cycle Subscription Upgrade (Standard → Premium)

**As a** Standard subscriber, **I want** a self-serve "Upgrade to Premium" flow on the Billing page —
CTA, proration preview, confirmation, and immediate plan/quota flip on payment success — **so that**
I can move to Premium mid-cycle for exactly the prorated amount, without leaving the app.

**Acceptance Criteria**

- AC1: Billing page shows an "Upgrade to Premium" button only when `billing_data[email]["plan_name"] == "Standard"`; hidden for `"Premium"`.
- AC2: The hardcoded `<span className="standard-badge">Standard</span>` (Billing.jsx line 128) is replaced by a value driven by `data.plan_name`; the plan card's "Active" badge and price reflect the real plan.
- AC3: Clicking the CTA opens a confirmation modal (no page navigation) showing: current plan (Standard, $20/mo), new plan (Premium, $40/mo), days remaining in the cycle, the prorated charge, and the next renewal price/date. "Cancel" closes it with no backend calls and no data changes.
- AC4: `GET /api/billing/upgrade-preview?email=<email>` returns `{current_plan, new_plan, days_remaining, prorated_charge, next_renewal_price, renew_at}`, computed server-side only: `days_remaining = max(1, (renew_at_date - today).days)`, `daily_delta = (40 - 20) / 30`, `prorated_charge = round(daily_delta * days_remaining, 2)`, with `renew_at` parsed via `datetime.strptime(renew_at, "%b %d, %Y")`. The frontend only renders this value — it never recomputes proration itself.
- AC5: `POST /api/billing/upgrade` (body `{"email": str}`) calls `charge_card(email, prorated_charge)`, a deterministic in-repo function: emails starting with `fail` → `{"status": "card_declined", "message": "Your card was declined."}`; every other email → `{"status": "success"}`. No external payment SDK or network dependency is introduced.
- AC6 (happy path): on `charge_card` success — `users[email]["plan"]` → `"Premium"`, `["price"]` → `"$40/month"`; `billing_data[email]["plan_name"]` → `"Premium"`, `["price"]` → `"$40/month"`; `billing_data[email]["usages"]` → Premium quotas (chat credits 10,000, chatbots 10, document pages 5,000 — `used` values unchanged); `on_demand_usage.notice` → `"On-demand credit is available on your Premium plan."`; `renew_at` is left unmodified. Endpoint returns `{"status": "success", "plan": "Premium", "charge": <amount>}`. Billing page re-fetches `GET /api/billing`, shows Premium plan/badge/price/quotas, hides the upgrade button, and shows a success banner `"You're now on Premium! $X.XX was charged."`.
- AC7 (failure path): on `charge_card` card_declined — endpoint returns HTTP 402 `{"detail": "card_declined", "message": "Your card was declined."}`; no mutation to `users` or `billing_data`; the modal shows the error inline and stays open so the user can cancel; user remains on Standard.
- AC8 (already-Premium guard): for a caller with `plan_name == "Premium"`, both `GET /api/billing/upgrade-preview` and `POST /api/billing/upgrade` return HTTP 409 `{"detail": "already_premium"}`, and the Billing page renders no upgrade button.
- AC9: No changes to auth, tasks, login, or registration flows.

**Covers**: REQ-F-01 .. REQ-F-13, REQ-NF-01 .. REQ-NF-04 (all — single-story cycle, full epic coverage)
**Requires**: none
**Files**: `backend/main.py` (`PLANS`, `PREMIUM_QUOTAS`, `DAYS_IN_CYCLE`, `UpgradeRequest`, `charge_card`, `GET /api/billing/upgrade-preview`, `POST /api/billing/upgrade`), `frontend/src/pages/Billing.jsx` (dynamic badge, CTA, modal, upgrade call, success/error banners)
