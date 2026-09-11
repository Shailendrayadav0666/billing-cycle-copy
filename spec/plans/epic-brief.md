# Epic Brief — Mid-Cycle Subscription Upgrade (Standard → Premium)

> **Source**: Helix solution document (fetched via `mcp__helix__get_solution_document_tool`)
> **Document ID**: 3157 · **Title**: "Epic: Mid-Cycle Subscription Upgrade (Standard → Premium).md"
> **Artifact type**: epic · **Version**: 1 · **Fetched**: 2026-09-11T09:01:49Z

## Problem Statement

The Billing page currently shows a hardcoded `Standard` badge and a static plan card with no upgrade
path. An active Standard subscriber ($20/mo) has no way to move to Premium ($40/mo) from within the
application — even though `billing_data` and `users` in `backend/main.py` already carry `plan_name`
and `price` fields designed to reflect the current plan.

This epic adds a self-serve upgrade flow: an **Upgrade Plan** CTA on the Billing page, a confirmation
step showing the prorated charge, and a dummy in-repo payment gateway that deterministically exercises
both the success and card-declined paths. No external payment SDK is involved.

## Goals

- Allow a Standard subscriber to upgrade to Premium in a single self-serve flow from the Billing page
- Charge only the prorated amount for days remaining in the current cycle at the time of upgrade
- Flip the plan to Premium immediately on payment success and update all quota values in `billing_data`
- Keep the user on Standard with a visible error on payment failure (card_declined)
- Keep everything demo-able locally with no external dependencies

## Out of Scope

- Downgrades (Premium → Standard)
- Refunds or credits
- Enterprise tier
- Real payment provider integration (Stripe, Braintree, etc.)
- Email receipts / notifications

## Pricing & Proration Specification

| Plan | Monthly Price |
|------|--------------|
| Standard | $20.00 |
| Premium | $40.00 |

```
days_remaining  = (renew_at_date - today).days          # integer, >= 1
days_in_cycle   = 30                                     # fixed for POC
daily_delta     = (premium_price - standard_price) / days_in_cycle
prorated_charge = daily_delta x days_remaining
```

Example: 15 days remaining -> `($40 - $20) / 30 * 15 = $10.00`

`renew_at` is stored in `billing_data` as a formatted string (`"Sep 09, 2025"`), parsed with
`datetime.strptime(renew_at, "%b %d, %Y")`.

## Dummy Payment Gateway Specification

`def charge_card(email: str, amount: float) -> dict` — deterministic on a trigger email prefix:

| Email prefix | Result |
|---|---|
| Not starting with `fail` | `{"status": "success"}` |
| Starting with `fail` (e.g. `fail@example.com`) | `{"status": "card_declined", "message": "Your card was declined."}` |

## User Stories (5)

1. **Upgrade CTA on Billing Page** — dynamic plan badge + conditional "Upgrade to Premium" button.
2. **Proration Confirmation Modal** — `GET /api/billing/upgrade-preview` + modal showing exact charge.
3. **Execute Upgrade & Dummy Payment** — `POST /api/billing/upgrade`, success/failure paths.
4. **Premium Plan Quotas & Billing Data** — quota bump (chat credits, chatbots, doc pages) on upgrade.
5. **Already-Premium Guard** — HTTP 409 guard on both endpoints + CTA hidden for Premium users.

Full technical design (Pydantic models, constants, endpoint contracts, proration code, exact
files/lines touched) is preserved verbatim in the source Helix document (id 3157) and is treated as
authoritative input to Requirements Analysis and the per-story implementation plans.

## Story Summary & Effort Estimates

| # | Story | Effort |
|---|-------|--------|
| 1 | Upgrade CTA on Billing Page | 0.5 day |
| 2 | Proration Confirmation Modal | 1 day |
| 3 | Execute Upgrade & Dummy Payment | 1 day |
| 4 | Premium Quotas & Billing Data | 0.5 day |
| 5 | Already-Premium Guard | 0.5 day |
| **Total** | | **~3.5 days** |

## Referenced Paths (from source analysis)

- `backend/main.py` — data structures (`users`, `billing_data`), plan fields, `renew_at` format, endpoints
- `frontend/src/pages/Billing.jsx` — hardcoded "Standard" badge (line 128), plan card, fetch pattern
- `frontend/src/context/AuthContext.jsx` — token = email pattern used across all API calls
