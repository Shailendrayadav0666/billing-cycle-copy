# Requirements: Mid-Cycle Subscription Upgrade (Standard → Premium)

## Intent Analysis Summary

- **User Request**: "using aire and helix mcp fetch the solution document and start implementing the epic requirements" — the Epic and Deep Dive were fetched from the Helix MCP (Atlas-backed solution documents) and are the primary input to this document.
- **Request Type**: New Feature (self-serve mid-cycle plan upgrade) on an existing brownfield POC.
- **Scope Estimate**: Multiple Components — 2 new backend endpoints + 1 new backend function + 1 frontend page (`Billing.jsx`) modified across 5 stories.
- **Complexity Estimate**: Moderate — no new infra/dependencies, but real proration math, a two-outcome dummy payment gateway, and multiple guarded states (Standard / Premium / already-Premium / declined).
- **Parent Epic**: `EPIC-LOCAL-1` (LOCAL tracker) — see `spec/plans/epic-brief.md` for the full source document (Helix solution document_id 3157).
- **Existing-System Context**: `spec/plans/deep-dive.md` (Helix solution document_id 3155, exhaustive, 13/13 steps) — Atlas coverage is Full; no local Reverse Engineering was run.
- **Context Project artifacts consulted**: none (user opted out — Context Opt-In answer "No, use the Epic + Deep Dive only").
- **Extension Configuration**: Security Baseline and Playwright Test Automation are always-on (mandatory). Resiliency Baseline and Property-Based Testing were both declined by the user for this POC (see `## Extension Configuration` in `runtime-artifacts/aire-state.md`).

---

## System Context (from Atlas / Deep Dive)

- **Stack**: React 19 + Vite frontend, FastAPI (Python) backend, in-memory dict-based data store (`users`, `billing_data`) — no database.
- **Auth**: email-as-bearer-token (existing POC pattern) — `AuthContext.jsx` stores the user's email as `token`; every API call passes it. This epic makes no auth changes.
- **Files in scope**: `backend/main.py`, `frontend/src/pages/Billing.jsx`, `frontend/src/context/AuthContext.jsx` (read-only reference for the token pattern).
- **Existing endpoints untouched by this epic**: `/api/auth/login`, `/api/auth/register`, `/api/users/me`, `/api/tasks` (GET/POST).
- **Existing `billing_data` shape** already carries `plan_name`, `price`, `renew_at` (string, format `"%b %d, %Y"`), `usages` (list of quota objects), `on_demand_usage.notice`.

---

## Functional Requirements

| ID | Requirement | Source |
|---|---|---|
| REQ-F-01 | The Billing page MUST display an "Upgrade to Premium" button when the current user's `plan_name` is `"Standard"`, and MUST NOT display it when `plan_name` is `"Premium"`. | Epic Story 1, Story 5 |
| REQ-F-02 | The hardcoded `"Standard"` badge in `Billing.jsx` (line 128) MUST be replaced with a value driven dynamically by the `GET /api/billing` response (`plan_name`). | Epic Story 1, Story 4 |
| REQ-F-03 | The plan card's "Active" badge and displayed price MUST always reflect the real current plan from `billing_data`, both before and after an upgrade. | Epic Story 1, Story 4 |
| REQ-F-04 | Clicking "Upgrade to Premium" MUST open a confirmation modal/panel (no page navigation) showing: current plan + price, new plan + price, days remaining in the cycle, the prorated charge amount, and the next renewal price/date. | Epic Story 2 |
| REQ-F-05 | The confirmation view's prorated charge and days-remaining values MUST be fetched from the backend (`GET /api/billing/upgrade-preview?email=<email>`), never computed client-side. | Epic Story 2 |
| REQ-F-06 | `GET /api/billing/upgrade-preview` MUST return `current_plan`, `new_plan`, `days_remaining`, `prorated_charge`, `next_renewal_price`, `renew_at` as specified in the Epic's response shape. | Epic Story 2 |
| REQ-F-07 | The confirmation modal MUST offer exactly two actions: "Confirm Upgrade" and "Cancel". Cancel MUST close the modal with zero side effects (no backend call). | Epic Story 2 |
| REQ-F-08 | The backend MUST compute the prorated charge server-side using: `days_remaining = max(1, (renew_at_date - today).days)`, `daily_delta = (Premium.price - Standard.price) / 30`, `prorated_charge = round(daily_delta * days_remaining, 2)`, parsing `renew_at` with `datetime.strptime(renew_at, "%b %d, %Y")`. | Epic Pricing & Proration Spec |
| REQ-F-09 | A new function `charge_card(email: str, amount: float) -> dict` MUST return `{"status": "success"}` for any email not starting with `"fail"`, and `{"status": "card_declined", "message": "Your card was declined."}` for any email starting with `"fail"`. | Epic Dummy Payment Gateway Spec |
| REQ-F-10 | On "Confirm Upgrade", the frontend MUST call `POST /api/billing/upgrade` with `{"email": "<email>"}`. | Epic Story 3 |
| REQ-F-11 | On a successful charge (`charge_card` returns `status: success`), the backend MUST: set `users[email]["plan"] = "Premium"` and `users[email]["price"] = "$40/month"`; set `billing_data[email]["plan_name"] = "Premium"` and `["price"] = "$40/month"`; update `billing_data[email]["usages"]` to the Premium quota values (REQ-F-14); update `billing_data[email]["on_demand_usage"]["notice"]` to remove the Standard restriction message; and return HTTP 200 with `{"status": "success", "plan": "Premium", "charge": <prorated_charge>}`. | Epic Story 3 |
| REQ-F-12 | After a successful upgrade, the frontend MUST re-fetch `GET /api/billing`, close the modal, hide the upgrade CTA, and show a success banner: `"You're now on Premium! $<charge>.00 was charged."` (exact charge amount interpolated). | Epic Story 3 |
| REQ-F-13 | On a declined charge (`charge_card` returns `status: card_declined`), the backend MUST make **no** mutation to `users` or `billing_data` and MUST return **HTTP 402** with `{"detail": "card_declined", "message": "Your card was declined."}`. The frontend MUST show this inline in the modal: `"Payment failed: Your card was declined. Your plan has not changed."`, and MUST keep the modal open so the user can cancel. | Epic Story 3 |
| REQ-F-14 | On successful upgrade, `billing_data[email]["usages"]` MUST be set to the Premium quota values: Chat credits total 10000 (was 2000), Chatbots total 10 (was 3), Document pages total 5000 (was 1000); each `used` count is reset to `0` per the Epic's `PREMIUM_QUOTAS` constant block. | Epic Story 4 |
| REQ-F-15 | On successful upgrade, `billing_data[email]["on_demand_usage"]["notice"]` MUST be updated to `"On-demand credit is available on your Premium plan."`. | Epic Story 4 |
| REQ-F-16 | `GET /api/billing/upgrade-preview` and `POST /api/billing/upgrade` MUST both guard against an already-Premium caller: if `billing_data[email]["plan_name"] == "Premium"`, return **HTTP 409** with `{"detail": "already_premium"}` and make no mutation. | Epic Story 5 |
| REQ-F-17 | `renew_at` MUST remain unchanged by the upgrade — the next full billing cycle still renews/bills on the original `renew_at` date. | Epic Acceptance Criteria — Epic Level |
| REQ-F-18 | No changes may be made to the auth, tasks, login, or registration flows/endpoints. | Epic Acceptance Criteria — Epic Level; Out of Scope |

## Non-Functional Requirements

| ID | Requirement | Source |
|---|---|---|
| REQ-NF-01 | All proration arithmetic MUST execute server-side; the frontend only renders values returned by the API — never recomputes them. | Epic Acceptance Criteria — Epic Level |
| REQ-NF-02 | The payment gateway MUST be fully deterministic and require no external service, SDK, network call, or environment secret — the `fail`-email-prefix rule is the only trigger for either outcome, enabling repeatable demos. | Epic Dummy Payment Gateway Spec |
| REQ-NF-03 | No new runtime dependency (pip or npm package) may be introduced — the epic's own Technical Design Notes confirm the required Python (`datetime`, already imported patterns) and React primitives (`useState`) are already available in the codebase. | Epic Referenced Paths — Low Relevance |
| REQ-NF-04 | Error responses (`402` card-declined, `409` already-premium) MUST use FastAPI's standard `HTTPException` / JSON-detail convention already used elsewhere in `backend/main.py`, so behavior is consistent with existing endpoints. | Deep Dive: existing API conventions |
| REQ-NF-05 | Because the app has no test suite (per Deep Dive Top Findings) and no database, the change must remain safely demonstrable purely via the in-memory store — a server restart resetting to Standard for all users is accepted/expected POC behavior and is NOT a defect to fix in this epic. | Deep Dive: Executive Summary / Top Findings |

---

## Out of Scope (carried from Epic — do not implement)

- Downgrades (Premium → Standard)
- Refunds or credits
- Enterprise tier
- Real payment provider integration (Stripe, Braintree, etc.)
- Email receipts / notifications

---

## Design References Consulted

None registered — the user opted out of both Context Project inputs (existing-knowledge and new-references) at Workspace Detection Step 4.7. All requirements above trace directly to the Helix-fetched Epic (`spec/plans/epic-brief.md`) and Deep Dive (`spec/plans/deep-dive.md`).

## Traceability

Every `REQ-F-*` / `REQ-NF-*` ID above is permanent and will be referenced by `stories.md` (`Covers`), the dependency graph, and code-generation/code-review artifacts per `common/requirements-traceability.md`.
