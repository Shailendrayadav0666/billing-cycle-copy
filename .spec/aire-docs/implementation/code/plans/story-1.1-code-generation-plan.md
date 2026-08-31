# Code Generation Plan — Story 1.1

**Story**: 1.1 — Mid-Cycle Subscription Upgrade (Standard → Premium) · `LOCAL` · 🔵 In Development
**Branch**: `story/1.1-mid-cycle-subscription-upgrade` (cut from `epic/EPIC-1-mid-cycle-subscription-upgrade`)
**AIRE**: v1.0 · **Status**: 🤖 auto-approved — announced and executed, no gate

---

## Grounding

Every step below traces to an approved artifact. No scope, file or behaviour is invented.

| Source | Used for |
|---|---|
| `stories.md` Story 1.1 | 31 acceptance criteria AC-1..AC-31 |
| `requirements.md` | FR-1..FR-13, NFR-1..NFR-7, SEC-1..SEC-6, findings F-1..F-6 |
| `epic-brief.md` (Atlas 3157) | Endpoint contracts, proration spec, gateway spec, copy |
| `functional-design/*` | D-1, D-2, D-3; BR-1..BR-10; function and endpoint designs |
| `nfr-design/*` | Patterns P-1..P-7; logical units and their NFR ownership |
| `.spec/architecture.md` | Section 3 layering rules; Section 10 constraints ARCH-01..ARCH-06 |
| `knowledge-graph.md` (Atlas 3155) | Existing code shape, conventions, call patterns |

### Design reference grounding (DR-5)

`### Reconciliations` read first (DR-8). Two points are already settled and are **not reopened**:
repo layout (`src/backend/` + `src/frontend/`), and `renew_at` being dynamic rather than the Epic's
fixture date.

- **`src/backend/main.py`** — Design reference: Atlas doc 3155 + 3157 — **grounded** (existing dict shapes, `renew_at` format, the 401 pattern used by all 6 existing endpoints, Pydantic model style).
- **`src/frontend/src/pages/Billing.jsx`** — Design reference: Atlas doc 3157 — **grounded** (the hardcoded badge at line 128, plan-card layout, fetch pattern, state shape). No wireframe or mockup exists (`## Context Project` → New References: No), so layout follows the page's own existing conventions.
- **`src/frontend/src/App.css`** — Design reference: none covers this component. New classes follow the file's existing flat-class convention.

### REQ-ID thread

Story 1.1 covers **every** requirement ID in `requirements.md`: FR-1..FR-13, NFR-1..NFR-7,
SEC-1..SEC-6 (26 IDs). Trace completeness self-check is at the end of this plan.

---

## Implementation order

Backend first. **AC-15 forbids the frontend computing the amount**, so the UI has nothing real to
render until `upgrade-preview` exists.

---

## Part A — Behaviour spec FIRST (the contract, before any code)

- [ ] **A1** Write `.spec/aire-docs/implementation/code/behavior/story-1.1.feature` — Gherkin for every scenario class, tagged `@AC-nn`. Authored **before** the implementation, because it is the contract the code must satisfy.
      *Traces*: all 31 ACs
- [ ] **A2** Write `tests/behavior/test_story_1_1.py` — pytest-bdd step definitions binding the feature to the real app via `TestClient`.
      *Traces*: NFR-M6 prep, behaviorScenarioPassRateMin

---

## Part B — Backend: `src/backend/main.py`

- [ ] **B1** Add the constant block after the imports: `PLANS`, `PREMIUM_QUOTA_TOTALS` (an `id → total` map, **not** the Epic's full-object list — decision **D-3**), `DAYS_IN_CYCLE = 30`, `PREMIUM_ON_DEMAND_NOTICE`.
      *Traces*: FR-13 → AC-21, AC-22 · NFR-3
- [ ] **B2** Add `class UpgradeRequest(BaseModel)` with **exactly one field**, `email: str`. No amount, price or card field — pattern **P-4**, absence of capability.
      *Traces*: FR-6, SEC-3, SEC-6 → AC-18
- [ ] **B3** Add `charge_card(email: str, amount: float) -> dict` — pure, deterministic, no I/O, no logging, no network. `fail` prefix → `card_declined`, else `success`.
      *Traces*: FR-12, SEC-4 → AC-16, AC-17
- [ ] **B4** Add `_resolve_upgrade_context(email) -> tuple[dict, int, float]` — the **single** implementation of the 401 → 404 → 409 guard chain and the proration formula. Pattern **P-1**; guard order is load-bearing.
      *Traces*: FR-4, FR-9, NFR-3, SEC-1, SEC-2 → AC-6, AC-7, AC-8, AC-9, AC-10, AC-11
- [ ] **B5** Add `_premium_usages(existing) -> list[dict]` — pure transform, returns a **new** list, spreads each entry so `id`/`label`/`used` survive by default. Unknown `id` passes through untouched. `documents-pages` help recomputed as `total - used` (BR-6). Pattern **P-3**.
      *Traces*: FR-13 → AC-21, AC-22
- [ ] **B6** Add `GET /api/billing/upgrade-preview` — read-only, composes B4, returns the 6-field quote.
      *Traces*: FR-4, FR-6 → AC-5, AC-6, AC-7, AC-10
- [ ] **B7** Add `POST /api/billing/upgrade` — the **only** writer. Three zones (**D-2** / **P-2**): Zone A validate + charge + the 402 `JSONResponse` return; Zone B build; Zone C the 6 contiguous dict assignments. `renew_at` preserved **by omission**.
      *Traces*: FR-7, FR-8, FR-11, NFR-5 → AC-19..AC-26
- [ ] **B8** Import `JSONResponse` from `fastapi.responses` — required because `HTTPException(detail=...)` cannot emit the 402's two-key body without nesting. **Stdlib/FastAPI only; no new dependency** (ARCH-05).
      *Traces*: FR-8 → AC-24, AC-26

🔴 **Not touched**: the 6 existing endpoints, `GET /api/billing`'s seed-user fallback (F-3), the static
mount (F-4), the dead `TokenRequest` (F-6), auth, tasks, login, registration.

---

## Part C — Frontend: `src/frontend/src/pages/Billing.jsx`

- [ ] **C1** Replace the hardcoded `<span className="standard-badge">Standard</span>` at line 128 with `{data.plan_name}`. Class name **kept** — a styling hook, not a semantic claim.
      *Traces*: FR-1 → AC-1
- [ ] **C2** Confirm the plan card renders `{data.price}`; keep the `"Active"` badge literal (a subscription-status label, accurate on both plans).
      *Traces*: FR-3 → AC-2
- [ ] **C3** Add `upgrade` state `{open, preview, loading, error}` and separate `success` state — separate because the banner outlives the modal.
      *Traces*: FR-5, FR-10
- [ ] **C4** Add the conditional CTA, strict `data.plan_name === 'Standard'`.
      *Traces*: FR-2 → AC-3, AC-4
- [ ] **C5** Add `openUpgrade()` — fetches the preview in `try/catch/finally` (**P-7**).
      *Traces*: FR-5 → AC-12
- [ ] **C6** Add `confirmUpgrade()` — POSTs, on 200 re-fetches billing + sets `success` + closes; on 402 keeps the modal open with the inline error. `finally` always clears `loading`.
      *Traces*: FR-10 → AC-27..AC-31
- [ ] **C7** Add `UpgradeModal` — the 5 display rows, Confirm/Cancel, error slot, `role="dialog"`, Escape, focus management, `role="alert"`. **Cancel stays enabled during a request** so a hung call cannot trap the user (AC-31).
      *Traces*: FR-5, FR-10 → AC-13, AC-14, AC-30, AC-31
- [ ] **C8** Add `UpgradeSuccessBanner` with the Epic's copy and `role="status"`.
      *Traces*: FR-10 → AC-29
- [ ] **C9** Add the 8 CSS classes to `src/frontend/src/App.css`. No existing class redefined.
      *Traces*: presentation only

🔴 **No pricing arithmetic anywhere in `Billing.jsx`** — `.toFixed(2)` formatting only (ARCH-02, AC-15).
🔴 The existing billing fetch at lines 105-107 is **left as-is** (F-5, out of scope), so the file will
temporarily hold two error-handling patterns.

---

## Part D — Unit tests: `tests/unit/`

- [ ] **D1t** `test_proration.py` — the formula **exhaustively over `days_remaining` 1..30**, plus the invariants and the `max(1, ...)` floor.
      *Traces*: NFR-C1, NFR-C2, NFR-C3, NFR-C4 → AC-6, AC-7
- [ ] **D2t** `test_charge_card.py` — determinism, `fail` prefix, case sensitivity, purity, no I/O.
      *Traces*: FR-12 → AC-16, AC-17
- [ ] **D3t** `test_premium_usages.py` — `used`/`label`/`id` preserved, totals raised, input list **not mutated**, unknown `id` passthrough, `documents-pages` help recomputed.
      *Traces*: FR-13, NFR-C7, NFR-M4 → AC-21, AC-22
- [ ] **D4t** `test_upgrade_preview.py` — 200 shape, 401, 404 (no seed-user fallback), 409.
      *Traces*: FR-4, FR-9, SEC-1, SEC-2 → AC-5, AC-8, AC-9, AC-10
- [ ] **D5t** `test_upgrade_execute.py` — happy path fields, Premium quotas, notice, **both** `renew_at` copies unchanged, 409.
      *Traces*: FR-7, FR-11, FR-13 → AC-19..AC-23
- [ ] **D6t** `test_upgrade_declined.py` — 402 exact body, and a **deep snapshot compare proving nothing mutated**.
      *Traces*: FR-8, NFR-5, SEC-5 → AC-24, AC-25, AC-26
- [ ] **D7t** `test_price_injection.py` — an `amount` in the request body is **ignored**; the server-computed value is charged.
      *Traces*: SEC-6 → AC-18
- [ ] **D8t** `conftest.py` — fixtures that snapshot and restore the module-level dicts between tests, so tests cannot leak state into each other.

🔴 **No test asserts a literal dollar amount** derived from a fixed `renew_at` (NFR-C4) — `renew_at` is
dynamic (F-1). Tests assert the formula and its invariants.

---

## Part E — Gates (in order, each self-healing capped at 3 attempts)

- [ ] **E1** Unit tests + coverage ≥ `unitTestCoverageMin` — SH-LOOP-1
- [ ] **E2** 🥒 Gherkin B1 + B2 — SH-LOOP-7. B3 is N/A: `.spec/behavior.feature` is deliberately scenario-free (one work unit)
- [ ] **E3** API & contract gate — SH-LOOP-2. **Applicable**: the story adds two endpoints
- [ ] **E4** Full regression vs baseline — SH-LOOP-3. Baseline had **no tests**, so this covers only this story's tests
- [ ] **E5** Static D1-D7 vs baseline — SH-LOOP-4. D2 and D6 will genuinely run now that Python changes exist
- [ ] **E6** Automated Code Review + diff-scoped Security Baseline review + blocking J1/J2 — SH-LOOP-6, SH-LOOP-5
- [ ] **E7** Commit, push, PR into the epic branch, auto PR review

---

## Trace completeness self-check (blocking, fixed silently before announcing)

| Requirement | Covered by plan step(s) |
|---|---|
| FR-1 | C1 |
| FR-2 | C4 |
| FR-3 | C2 |
| FR-4 | B4, B6, D4t |
| FR-5 | C3, C5, C7 |
| FR-6 | B2, B6, C7 |
| FR-7 | B7, D5t |
| FR-8 | B7, B8, D6t |
| FR-9 | B4, D4t |
| FR-10 | C3, C6, C7, C8 |
| FR-11 | B7, D5t |
| FR-12 | B3, D2t |
| FR-13 | B1, B5, D3t, D5t |
| NFR-1 | B8 (no new dependency), E5 |
| NFR-2 | B3 |
| NFR-3 | B1, B4, D1t |
| NFR-4 | D1t (formula, not literals) |
| NFR-5 | B7, D6t |
| NFR-6 | E1 |
| NFR-7 | post-merge Playwright |
| SEC-1 | B4, D4t |
| SEC-2 | B4, D4t |
| SEC-3 | B2 |
| SEC-4 | B3, E6 |
| SEC-5 | B7, D6t |
| SEC-6 | B2, B7, D7t |
| **AC-1..AC-31** | every AC appears in ≥1 step above |

✅ **26/26 requirement IDs and 31/31 ACs each appear in at least one step. Check passes.**

**Total steps**: 8 backend · 9 frontend · 8 test · 2 behaviour · 7 gates = **34**
