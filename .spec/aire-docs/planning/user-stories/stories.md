EPIC TICKET: EPIC-1 — Mid-Cycle Subscription Upgrade (Standard → Premium) · LOCAL tracker, no external URL · source: Atlas solution document 3157

---

# User Stories — EPIC-1

**Tracker**: LOCAL · **team_size**: 2 · **story_creation_mode**: all-at-once
**target_story_count**: **1** — user-directed override of the recommended 10, explicitly confirmed
**Created**: 2026-08-31

> ⚠️ **Accepted deviation from the Step 1.5 sizing ceilings.** The user was shown the full trade-off
> (parallelism broken, ~30 ACs against a ceiling of 5, both architectural layers, all four scenario
> classes, one self-healing budget for the whole Epic) and deliberately chose a single story. Recorded
> in `audit.md` Entries 10–11. The ACs below are grouped by concern purely for readability — they are
> all acceptance criteria of the one story.

---

## Story 1.1 — Mid-Cycle Subscription Upgrade (Standard → Premium)

| Field | Value |
|---|---|
| **Story ID** | 1.1 |
| **Tracker ID** | LOCAL |
| **Status** | 🟢 Ready for Development |
| **Personas** | P1 Standard Subscriber (primary) · P2 Premium Subscriber (guard) · P3 Demo Presenter (declined path) |
| **Requires** | *(assigned by the Dependency Graph stage — expected: none)* |
| **Scope** | `src/backend/main.py` · `src/frontend/src/pages/Billing.jsx` |

### Narrative

**As a** Standard subscriber ($20/month),
**I want** to upgrade to Premium ($40/month) from the Billing page, paying only the prorated amount for the days remaining in my current cycle,
**so that** I get the Premium quotas immediately without waiting for my next renewal or contacting support.

**And as a** Premium subscriber, **I want** no upgrade prompt and no way to be charged twice.
**And as a** demo presenter, **I want** the card-declined path to be reproducible on demand with no external payment provider.

### Acceptance Criteria

#### Group A — Billing page reflects the real plan *(FR-1, FR-3)*

- **AC-1** The `"Current plan:"` label renders `data.plan_name` from the `GET /api/billing` response. The hardcoded `<span className="standard-badge">Standard</span>` at `Billing.jsx:128` is gone; a Premium user sees `Premium` there.
- **AC-2** The plan card's price renders `data.price`, and its `"Active"` badge reflects the real plan rather than being hardcoded.

#### Group B — Upgrade CTA eligibility *(FR-2)*

- **AC-3** An "Upgrade to Premium" button is rendered on the Billing page **if and only if** `data.plan_name === "Standard"`.
- **AC-4** When `data.plan_name === "Premium"` no upgrade button appears anywhere on the page.

#### Group C — Prorated quote endpoint *(FR-4, FR-6, NFR-3, SEC-1, SEC-2)*

- **AC-5** `GET /api/billing/upgrade-preview?email=<email>` returns HTTP 200 with exactly `current_plan`, `new_plan`, `days_remaining`, `prorated_charge`, `next_renewal_price`, `renew_at`.
- **AC-6** `days_remaining` is derived from the stored `renew_at` parsed with `datetime.strptime(renew_at, "%b %d, %Y")`, floored at 1: `max(1, (renew_at_date - datetime.today()).days)`.
- **AC-7** `prorated_charge` equals `round(((40.0 - 20.0) / 30) * days_remaining, 2)`. `next_renewal_price` is `40.0`. `renew_at` is echoed unchanged.
- **AC-8** The endpoint returns HTTP 401 when `email not in users`, matching the existing endpoints' behaviour.
- **AC-9** The endpoint returns HTTP 404 when the caller has no `billing_data` entry. It **must not** fall back to another user's record — the `billing_data.get(email, billing_data["tpg@example.com"])` pattern at `main.py:188` is **not** reproduced (finding F-3).

#### Group D — Already-Premium guard *(FR-9)*

- **AC-10** `GET /api/billing/upgrade-preview` returns HTTP 409 `{"detail": "already_premium"}` when the caller's `plan_name` is `"Premium"`.
- **AC-11** `POST /api/billing/upgrade` returns HTTP 409 `{"detail": "already_premium"}` when the caller's `plan_name` is `"Premium"`, and mutates nothing.

#### Group E — Confirmation modal *(FR-5, FR-6)*

- **AC-12** Clicking the CTA opens a modal or inline confirmation panel with **no page navigation**, populated from `GET /api/billing/upgrade-preview`.
- **AC-13** The modal displays: current plan `Standard ($20/mo)` · new plan `Premium ($40/mo)` · days remaining · the prorated charge as `You will be charged $<amount> today` · `$40.00/month starting <renew_at>`.
- **AC-14** The modal offers **Confirm Upgrade** and **Cancel**. Cancel closes it with no request sent and no state changed.
- **AC-15** The frontend never computes the prorated amount — it renders only the value returned by the API (verified by the absence of any pricing arithmetic in `Billing.jsx`).

#### Group F — Dummy payment gateway *(FR-12, SEC-4, SEC-6)*

- **AC-16** `charge_card(email: str, amount: float) -> dict` exists in `src/backend/main.py`. An email starting with `fail` returns `{"status": "card_declined", "message": "Your card was declined."}`; any other email returns `{"status": "success"}`.
- **AC-17** The gateway makes no network call, imports no payment SDK, and adds no dependency. It accepts no card data, and neither it nor the endpoints log the email or the amount.
- **AC-18** The charged amount is always computed server-side. The `POST /api/billing/upgrade` request body accepts **only** `{"email": str}` — a client-supplied amount is impossible.

#### Group G — Upgrade happy path *(FR-7, FR-11, FR-13, NFR-5)*

- **AC-19** `POST /api/billing/upgrade` with a non-`fail` email returns HTTP 200 `{"status": "success", "plan": "Premium", "charge": <prorated_charge>}`, where `charge` equals what `upgrade-preview` would return at that moment.
- **AC-20** On success `users[email]["plan"] == "Premium"`, `users[email]["price"] == "$40/month"`, `billing_data[email]["plan_name"] == "Premium"`, `billing_data[email]["price"] == "$40/month"`.
- **AC-21** On success `billing_data[email]["usages"]` becomes Premium quotas: chat credits total **10,000**, chatbots total **10**, document pages total **5,000** — preserving each entry's `id`, `label` and existing `used` value.
- **AC-22** On success `billing_data[email]["on_demand_usage"]["notice"]` becomes `"On-demand credit is available on your Premium plan."`
- **AC-23** `renew_at` is **unchanged** by the upgrade, in both `users[email]` and `billing_data[email]` — the next full cycle still bills at the original renewal date.

#### Group H — Upgrade declined path *(FR-8, NFR-5, SEC-5)*

- **AC-24** `POST /api/billing/upgrade` with an email starting with `fail` returns HTTP **402** with `{"detail": "card_declined", "message": "Your card was declined."}`.
- **AC-25** After a declined attempt **not one field** of `users[email]` or `billing_data[email]` differs from its pre-request value — plan, price, quotas, notice and `renew_at` are all untouched.
- **AC-26** The 402 body carries only the fixed `card_declined` detail and message. No stack trace, internal state, or other user's data appears in it.

#### Group I — Frontend success handling *(FR-10)*

- **AC-27** On a successful upgrade the frontend re-fetches `GET /api/billing`, closes the modal, and the page shows Premium: the plan badge, the `$40/month` price, and the Premium quota totals.
- **AC-28** The upgrade CTA is no longer rendered after a successful upgrade.
- **AC-29** A success banner reads `You are now on Premium! $<amount> was charged.` with the actual charged amount.

#### Group J — Frontend failure handling *(FR-10)*

- **AC-30** On a 402 the modal **stays open** and shows, inline, `Payment failed: Your card was declined. Your plan has not changed.`
- **AC-31** After a failure the user can still Cancel to close the modal, and the Billing page still shows Standard with Standard quotas.

### Requirement trace

FR-1 → AC-1 · FR-2 → AC-3, AC-4 · FR-3 → AC-2 · FR-4 → AC-5 · FR-5 → AC-12, AC-13, AC-14 · FR-6 → AC-15, AC-18 · FR-7 → AC-19, AC-20 · FR-8 → AC-24, AC-25 · FR-9 → AC-9, AC-10, AC-11 · FR-10 → AC-27, AC-29, AC-30, AC-31 · FR-11 → AC-23 · FR-12 → AC-16, AC-17 · FR-13 → AC-21, AC-22
NFR-1 → AC-17 · NFR-2 → AC-17 · NFR-3 → AC-6, AC-7 · NFR-4 → *(gate-level: tests assert the formula, never a literal amount)* · NFR-5 → AC-25 · NFR-6, NFR-7 → *(gate-level)*
SEC-1 → AC-8 · SEC-2 → AC-9 · SEC-3 → AC-18 · SEC-4 → AC-17 · SEC-5 → AC-26 · SEC-6 → AC-18

### Out of scope for this story

Downgrades · refunds/credits · Enterprise tier · real payment providers · email receipts · any change to auth, tasks, login or registration · the pre-existing defects **F-4** (`dist_dir` resolves to `src/frontend/dist`), **F-5** (missing `.catch()` on the existing billing fetch), **F-6** (dead `TokenRequest` model).

### Definition of Done

- [ ] All 31 acceptance criteria demonstrably met
- [ ] Gherkin behaviour spec written **before** the code at `.spec/aire-docs/implementation/code/behavior/story-1.1.feature`
- [ ] Unit tests in `tests/unit/` meeting `unitTestCoverageMin`
- [ ] Behaviour gates B1/B2/B3 green
- [ ] API & contract gate green (the story adds two endpoints)
- [ ] Full regression green against the captured baseline
- [ ] Static D1–D7 green; blocking J1/J2 judge gates green
- [ ] Security Baseline diff-scoped review clean on the changed surface
- [ ] PR raised into `epic/EPIC-1-mid-cycle-subscription-upgrade` and auto-reviewed

---

## Requirements Coverage Matrix (Step 18.5)

| Requirement | Covered by | Fully covered |
|---|---|---|
| FR-1 | AC-1 | ✅ |
| FR-2 | AC-3, AC-4 | ✅ |
| FR-3 | AC-2 | ✅ |
| FR-4 | AC-5 | ✅ |
| FR-5 | AC-12, AC-13, AC-14 | ✅ |
| FR-6 | AC-15, AC-18 | ✅ |
| FR-7 | AC-19, AC-20 | ✅ |
| FR-8 | AC-24, AC-25 | ✅ |
| FR-9 | AC-9, AC-10, AC-11 | ✅ |
| FR-10 | AC-27, AC-29, AC-30, AC-31 | ✅ |
| FR-11 | AC-23 | ✅ |
| FR-12 | AC-16, AC-17 | ✅ |
| FR-13 | AC-21, AC-22 | ✅ |
| NFR-1 | AC-17 | ✅ |
| NFR-2 | AC-17 | ✅ |
| NFR-3 | AC-6, AC-7 | ✅ |
| NFR-4 | gate-level (test-authoring constraint) | ✅ |
| NFR-5 | AC-25 | ✅ |
| NFR-6 | gate-level (coverage threshold) | ✅ |
| NFR-7 | gate-level (Playwright extension) | ✅ |
| SEC-1 | AC-8 | ✅ |
| SEC-2 | AC-9 | ✅ |
| SEC-3 | AC-18 | ✅ |
| SEC-4 | AC-17 | ✅ |
| SEC-5 | AC-26 | ✅ |
| SEC-6 | AC-18 | ✅ |

**Coverage: 26/26 requirement IDs fully covered.**
