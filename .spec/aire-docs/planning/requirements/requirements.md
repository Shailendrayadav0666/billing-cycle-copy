# Requirements — Mid-Cycle Subscription Upgrade (Standard → Premium)

**Epic**: EPIC-1 (LOCAL) · sourced from Atlas solution document 3157
**Project**: Billing-Cycle (`helix-aire-v1-demo2`)
**Branch**: `epic/EPIC-1-mid-cycle-subscription-upgrade` (base `main`)
**AIRE Version**: 1.0
**Depth**: Standard (with requirement-level traceability)
**Author role**: Product Owner
**Created**: 2026-08-31

---

## 1. Grounding — inputs consulted

| Input | Path / ref | What it governs |
|---|---|---|
| **Epic brief** | `.spec/aire-docs/planning/requirements/epic-brief.md` (Atlas doc 3157) | **Primary** — defines WHAT to build: 5 stories, proration spec, gateway spec, epic-level ACs |
| **Knowledge graph** | `.spec/aire-docs/planning/reverse-engineering/knowledge-graph.md` (Atlas doc 3155) | Existing architecture, flows, data stores, API surface — the **starting state** |
| **Live code** | `src/backend/main.py`, `frontend/src/pages/Billing.jsx`, `frontend/src/context/AuthContext.jsx` | Verification of the Epic's stated assumptions |
| **Context Project** | — | Not used. User answered "no" to both existing-knowledge and new-references. |

**Design references consulted**: Atlas documents 3157 and 3155, both read in full (3155 lines 1–600; remainder pulled incrementally). See `aire-state.md` → `## Design References` for the reconciliation record.

---

## 2. Intent Analysis

| Dimension | Assessment |
|---|---|
| **Request clarity** | **Clear** — the Epic specifies endpoints, payloads, formulas, status codes and quota values |
| **Request type** | **New Feature** (extends an existing page and API) |
| **Scope estimate** | **Multiple Components** — backend API module + frontend Billing page |
| **Complexity estimate** | **Moderate** — small surface, but money-adjacent arithmetic, two failure branches, and guard conditions |
| **Risk / impact** | **Medium** — mutates billing state; must not touch auth, tasks, login or registration |

**Depth rationale**: Standard. The Epic is unusually well specified, so no elaboration is needed on *what* to build; requirement-level traceability is still carried because the change is money-adjacent and every acceptance criterion must map to a test.

---

## 3. Verification of the Epic against the live code

Everything below was checked against the real files, not inferred.

### 3.1 Confirmed

| # | Epic assumption | Verified |
|---|---|---|
| C-1 | `Billing.jsx` line 128 hardcodes the Standard badge | ✅ Exactly `Current plan: <span className="standard-badge">Standard</span>` |
| C-2 | `plan_name` / `price` already exist in `billing_data` and `users` | ✅ `main.py` lines 25–26, 33–34, 123–124, 128–129 |
| C-3 | `data.plan_name` is returned but not rendered | ✅ Plan card renders `data.price` (line 136) and a hardcoded `"Active"` badge (line 139) |
| C-4 | Token is the raw email and is used as the `email` query param | ✅ `AuthContext.jsx` line 25; `Billing.jsx` line 105 |
| C-5 | No new dependencies needed | ✅ `datetime` (line 6) and Pydantic `BaseModel` (line 4) already imported; Vite `/api` proxy already covers new routes |
| C-6 | `renew_at` string format is `"%b %d, %Y"` | ✅ Written with that exact format at lines 27, 35, 125, 130 |

### 3.2 Corrected — findings that change expected values

| # | Finding | Consequence for requirements |
|---|---|---|
| **F-1** | `renew_at` is **dynamic**, not the fixture `"Sep 09, 2025"`. It is `(datetime.today() + timedelta(days=30)).strftime("%b %d, %Y")`, recomputed at module import and at registration. | Requirements must not depend on a fixed date. |
| **F-2** | Because the parsed `renew_at` is midnight and `datetime.today()` carries a time, `days_remaining` evaluates to **29**, so the prorated charge is **$19.33**, not $10.00. | **The Epic's "$10.00" is an illustrative example of the formula, not an expected value.** Tests, Gherkin and UI assertions must assert *the formula*, not a literal amount. Captured as **NFR-4**. |
| **F-3** | `GET /api/billing` line 188 is `billing_data.get(email, billing_data["tpg@example.com"])` — a user with no billing record is served the **seed user's** record. | The two new endpoints must **not** inherit this fallback. Captured as **FR-9** and **SEC-2**. |
| **F-4** | `dist_dir` (line 210) resolves to `src/frontend/dist`, but the frontend is at repo-root `frontend/`. Pre-existing, caused by the AIRE restructure. | **Out of scope.** Flagged only; the Epic scopes out unrelated changes. |
| **F-5** | The billing fetch (lines 105–107) has no `.catch()`; a failure leaves "Loading billing..." on screen forever. | New calls must handle errors (**FR-10**). The existing fetch is adjacent pre-existing debt — noted, not silently rewritten. |
| **F-6** | `TokenRequest` (lines 97–98) is dead code. | Out of scope. |

---

## 4. Functional Requirements

| ID | Requirement | Source | Priority |
|---|---|---|---|
| **FR-1** | The Billing page renders the current plan name from the API response (`data.plan_name`), replacing the hardcoded `"Standard"` string. | Epic Story 1, 4 | Must |
| **FR-2** | The Billing page renders an "Upgrade to Premium" CTA **if and only if** `plan_name == "Standard"`. | Epic Story 1, 5 | Must |
| **FR-3** | The plan card's price and `"Active"` badge reflect the real plan from `billing_data`. | Epic Story 1, 4 | Must |
| **FR-4** | `GET /api/billing/upgrade-preview?email=<email>` returns `current_plan`, `new_plan`, `days_remaining`, `prorated_charge`, `next_renewal_price`, `renew_at`. | Epic Story 2 | Must |
| **FR-5** | Clicking the CTA opens a modal (no navigation) showing current plan, new plan, days remaining, prorated charge, and next renewal price + date, with **Confirm Upgrade** and **Cancel** actions. Cancel closes with no change. | Epic Story 2 | Must |
| **FR-6** | All proration arithmetic runs **server-side**. The frontend displays only what the API returns and never computes the amount. | Epic Story 2, epic-level AC | Must |
| **FR-7** | `POST /api/billing/upgrade` with `{"email": str}` calls `charge_card(email, prorated_charge)`. On `success`: set `users[email].plan`/`price` and `billing_data[email].plan_name`/`price` to Premium / `"$40/month"`, replace `usages` with Premium quotas, replace `on_demand_usage.notice`, and return `{"status":"success","plan":"Premium","charge":<amount>}`. | Epic Story 3, 4 | Must |
| **FR-8** | On `card_declined`: return **HTTP 402** with `{"detail":"card_declined","message":"Your card was declined."}` and mutate **nothing**. The user stays on Standard. | Epic Story 3 | Must |
| **FR-9** | Both new endpoints return **HTTP 409** `{"detail":"already_premium"}` when `plan_name == "Premium"`. Neither may fall back to another user's billing record (see F-3); a missing record is an error, not a substitution. | Epic Story 5 + F-3 | Must |
| **FR-10** | On success the frontend re-fetches `GET /api/billing`, closes the modal, hides the CTA, and shows the banner "You are now on Premium! $<amount> was charged." On failure it keeps the modal open and shows "Payment failed: Your card was declined. Your plan has not changed." | Epic Story 3 | Must |
| **FR-11** | `renew_at` is **preserved unchanged** by the upgrade — the next full cycle still bills at the original renewal date. | Epic-level AC | Must |
| **FR-12** | `charge_card(email, amount) -> dict` is a deterministic in-repo dummy gateway: emails starting with `fail` return `card_declined`; all others return `success`. No external SDK, no network call. | Epic gateway spec | Must |
| **FR-13** | Premium quotas after upgrade: Chat credits 10,000 · Chatbots 10 · Document pages 5,000. `on_demand_usage.notice` becomes `"On-demand credit is available on your Premium plan."` | Epic Story 4 | Must |

### 4.1 Explicitly out of scope

Downgrades · refunds/credits · Enterprise tier · real payment providers · email receipts/notifications · any change to auth, tasks, login or registration flows · the pre-existing defects F-4, F-5 (existing fetch), F-6.

---

## 5. Non-Functional Requirements

| ID | Requirement | Rationale |
|---|---|---|
| **NFR-1** | No new runtime dependencies, frontend or backend. | Epic constraint; verified feasible (C-5) |
| **NFR-2** | The whole flow is demonstrable locally with no external service. | Epic goal |
| **NFR-3** | Proration is computed as `round(((40.0 - 20.0) / 30) * max(1, days_remaining), 2)`, with `days_remaining` derived from the parsed `renew_at`. | Epic proration spec |
| **NFR-4** | Tests and behaviour specs assert the **formula and its invariants**, never the literal `$10.00`, because `renew_at` is dynamic (F-1, F-2). Invariants: charge > 0 · charge ≤ $20.00 · `days_remaining` ≥ 1. | F-2 |
| **NFR-5** | The upgrade mutation is **all-or-nothing**: on a declined card no field of `users` or `billing_data` is modified. | FR-8; money-adjacent correctness |
| **NFR-6** | Unit test coverage meets the project's `unitTestCoverageMin` threshold (set in `.evals/config.json` at the STOP CHECKPOINT). | AIRE gate |
| **NFR-7** | The Playwright Test Automation extension is mandatory — the UI-relevant paths get executable browser automation once the dev and ve PRs merge. | Always-mandatory extension |

---

## 6. Security Requirements (Security Baseline — always mandatory, blocking)

Scoped to the **changed surface** only; pre-existing baseline violations elsewhere are recorded, not fixed in this cycle.

| ID | Requirement | Baseline link |
|---|---|---|
| **SEC-1** | Both new endpoints authenticate the caller exactly as the existing endpoints do (`email not in users` → HTTP 401). No new endpoint is reachable unauthenticated. | Access control |
| **SEC-2** | Neither new endpoint may read or mutate a billing record belonging to a different email. The `billing_data.get(email, billing_data["tpg@example.com"])` fallback (F-3) must **not** be reproduced. | Access control / IDOR |
| **SEC-3** | The `email` body/query field is validated through Pydantic / FastAPI typing; the gateway's `fail` prefix check is a plain string comparison with no interpolation into any sink. | Input validation |
| **SEC-4** | No card data, no secrets and no credentials are accepted, logged or stored — the dummy gateway takes only an email and an amount. Nothing is written to logs. | Credential management / logging |
| **SEC-5** | The 402 error response returns only the fixed `card_declined` message — no internal state, stack trace or user data leaks into the error body. | Error handling |
| **SEC-6** | The amount charged is computed server-side and never accepted from the client, so a caller cannot choose their own price. | Input validation / business logic |

### 6.1 Pre-existing baseline findings — recorded, NOT in scope

Email-as-auth-token · plain-text passwords · `allow_origins=["*"]` with `allow_credentials=True` · credentials in query parameters · unpinned backend dependencies. All are documented in Atlas doc 3155 as critical, all pre-date this cycle, and the Epic explicitly scopes out auth changes. Fixing them is a separate cycle.

---

## 7. Traceability Matrix

| Epic-level AC | Requirements | Story |
|---|---|---|
| Standard subscriber sees "Upgrade to Premium" | FR-1, FR-2, FR-3 | 1 |
| Modal shows the exact prorated amount | FR-4, FR-5, FR-6, NFR-3 | 2 |
| Non-`fail` email succeeds: plan flips, quotas update, page refreshes, banner | FR-7, FR-10, FR-13 | 3, 4 |
| `fail*` email fails: stays Standard, error in modal, nothing mutated | FR-8, FR-10, NFR-5 | 3 |
| Already-Premium: no button, 409 on both endpoints | FR-2, FR-9 | 5 |
| `renew_at` preserved after upgrade | FR-11 | 3 |
| Gateway deterministic, no external service | FR-12, NFR-2 | 3 |
| Proration server-side only | FR-6, NFR-3, SEC-6 | 2 |
| No changes to auth, tasks, login, registration | Section 4.1 | all |

---

## 8. Assumptions

| # | Assumption | If wrong |
|---|---|---|
| A-1 | `$19.33` (not `$10.00`) is the amount a demo will actually show, because `renew_at` is `today + 30 days`. The Epic's $10.00 illustrates the formula. | If a fixed $10.00 is genuinely required, `renew_at` seeding must change — that is a new requirement, not part of this Epic. |
| A-2 | Only two plans exist (Standard, Premium). `PLANS` is a two-entry constant. | An Enterprise tier would need a general plan-ladder model — explicitly out of scope. |
| A-3 | In-memory dicts remain the data layer; no persistence is introduced. Upgrades are lost on server restart, as all data already is. | Introducing a database is a separate cycle. |
| A-4 | `DAYS_IN_CYCLE = 30` is fixed, matching the Epic, even though real months vary. | Calendar-accurate cycles would be a new requirement. |
| A-5 | The success banner and modal copy are taken verbatim from the Epic. | Copy changes are cosmetic and can be adjusted at review. |

---

## 9. Open Risks

| # | Risk | Severity | Mitigation |
|---|---|---|---|
| R-1 | Float arithmetic on money (`20.0 / 30`) can produce representation error. | Medium | `round(..., 2)` per the Epic spec; assert invariants (NFR-4) rather than exact floats. Decimal would be correct but deviates from the Epic's stated design — flagged for the design stage to decide. |
| R-2 | `days_remaining` truncation (F-2) is easy to misread as a bug during demo. | Low | Documented here and in the behaviour spec; the value is correct per the formula. |
| R-3 | The upgrade mutates several fields across two dicts with no transaction. A mid-mutation exception could leave a half-upgraded record. | Medium | NFR-5: charge first, then mutate; build the new state and assign, so a failure cannot partially apply. |
| R-4 | Zero existing tests means no regression safety net for the Billing page. | Medium | The cycle's D1–D7 baseline capture plus new unit tests establish the net. |
