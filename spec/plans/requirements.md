# Requirements — Mid-Cycle Subscription Upgrade (Standard → Premium)

**Depth**: Standard (the Epic is already fully specified with endpoint contracts, data shapes and a
proration formula; this document turns that into traceable REQ-IDs rather than re-deriving intent).
**Primary inputs**: `spec/plans/epic-brief.md`, `spec/plans/atlas-deep-dive.md` (existing system truth).

## Functional Requirements

| REQ-ID | Requirement | Source |
|---|---|---|
| REQ-F-01 | The Billing page displays an "Upgrade to Premium" button only when the caller's `plan_name == "Standard"`. | Epic Story 1 |
| REQ-F-02 | The hardcoded `<span className="standard-badge">Standard</span>` in `Billing.jsx` is replaced by a value driven by `data.plan_name` from the API response. | Epic Story 1 |
| REQ-F-03 | `GET /api/billing/upgrade-preview?email=<email>` returns `current_plan`, `new_plan`, `days_remaining`, `prorated_charge`, `next_renewal_price`, `renew_at` for a Standard subscriber. | Epic Story 2 |
| REQ-F-04 | Proration is computed server-side only: `days_remaining = max(1, (renew_at_date - today).days)`, `daily_delta = (40 - 20) / 30`, `prorated_charge = round(daily_delta * days_remaining, 2)`; `renew_at` is parsed with `datetime.strptime(renew_at, "%b %d, %Y")`. | Epic Pricing & Proration Specification |
| REQ-F-05 | Clicking "Upgrade to Premium" opens a confirmation modal (no navigation) showing current plan, new plan, days remaining, prorated charge, and next renewal price; the modal offers "Confirm Upgrade" and "Cancel". Cancel makes no backend calls and changes no data. | Epic Story 2 |
| REQ-F-06 | `POST /api/billing/upgrade` (body `{"email": str}`) calls `charge_card(email, prorated_charge)`. | Epic Story 3 |
| REQ-F-07 | `charge_card(email, amount)` is deterministic: emails starting with `fail` return `{"status": "card_declined", "message": "Your card was declined."}`; every other email returns `{"status": "success"}`. | Epic Dummy Payment Gateway Specification |
| REQ-F-08 | On `charge_card` success: `users[email]["plan"]` -> `"Premium"`, `users[email]["price"]` -> `"$40/month"`; `billing_data[email]["plan_name"]` -> `"Premium"`, `"price"` -> `"$40/month"`; `billing_data[email]["usages"]` updated to Premium quotas (REQ-F-10); `on_demand_usage.notice` updated; endpoint returns `{"status": "success", "plan": "Premium", "charge": <amount>}`. | Epic Story 3 |
| REQ-F-09 | On `charge_card` card_declined: endpoint returns HTTP 402 with `{"detail": "card_declined", "message": "Your card was declined."}`; no mutation to `users` or `billing_data`; the modal shows the error inline and stays open so the user can cancel. | Epic Story 3 |
| REQ-F-10 | Premium quotas after upgrade: chat credits 10,000 (was 2,000), chatbots 10 (was 3), document pages 5,000 (was 1,000); `used` values are unchanged by the upgrade itself. `on_demand_usage.notice` becomes `"On-demand credit is available on your Premium plan."`. | Epic Story 4 |
| REQ-F-11 | For a caller already on Premium: `GET /api/billing/upgrade-preview` and `POST /api/billing/upgrade` both return HTTP 409 `{"detail": "already_premium"}`, and the Billing page renders no "Upgrade to Premium" button. | Epic Story 5 |
| REQ-F-12 | After a successful upgrade, the Billing page re-fetches `GET /api/billing`, shows the Premium plan/badge/price/quotas, hides the upgrade button, and displays a success banner: `"You're now on Premium! $X.XX was charged."`. | Epic Story 3 |
| REQ-F-13 | `renew_at` is never modified by the upgrade — the existing renewal date and cycle length are preserved. | Epic Acceptance Criteria — Epic Level |

## Non-Functional / Constraint Requirements

| REQ-ID | Requirement | Source |
|---|---|---|
| REQ-NF-01 | No external payment SDK, network call, or dependency is introduced — `charge_card` is a pure in-repo function. | Epic Goals / Out of Scope |
| REQ-NF-02 | No changes to auth, tasks, login, or registration flows. | Epic Acceptance Criteria — Epic Level |
| REQ-NF-03 | All proration math is computed server-side; the frontend only renders values returned by the API — never recomputes them. | Epic Acceptance Criteria — Epic Level |
| REQ-NF-04 | Downgrades, refunds/credits, an Enterprise tier, and email receipts/notifications are explicitly out of scope for this epic. | Epic Out of Scope |

## Traceability

Every REQ-ID above maps 1:1 to an Epic story via the `Source` column; the Story-to-REQ `Covers` lines
are assigned when `stories.md` is written (next stage) so coverage is complete in both directions.
