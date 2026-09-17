# Functional Design — Self-Serve Premium Upgrade

Technology-agnostic business logic design for Story 1.1, built from `spec/plans/requirements.md` and
`spec/plans/stories.md`. No clarifying questions were needed — the Epic/PRD/requirements already
resolve every business-logic decision below.

---

## 1. Domain Model

No new persistent entities or schema. This story only adds new **field values** to the two existing
in-memory records (`atlas-deep-dive.md` "Database Analysis"):

```
users[email]:
  plan: "Standard" | "Premium"        # mutated by this story
  price: "$20/month" | "$50/month"    # mutated by this story
  (id, name, email, password, renew_at — unchanged by this story)

billing_data[email]:
  plan_name: "Standard" | "Premium"                       # mutated
  price: "$20/month" | "$50/month"                         # mutated
  renew_at: unchanged
  usages: [{ name, used, limit }]                          # `limit` mutated per the table below; `used` carried over unchanged
  included_usage: unchanged
  on_demand_usage: { available: bool, notice: string, ... }  # `notice` mutated; balance/available carried over unchanged (REQ-F-06 / Q2 decision)
```

**New request model** (`UpgradeRequest`, Pydantic, matching the existing `LoginRequest`/`RegisterRequest` style in `main.py`):

```python
class UpgradeRequest(BaseModel):
    email: EmailStr   # basic format validation — REQ-NF-05 / SECURITY-05; existing endpoints have
                       # none, but this is NEW code and the mandatory Security Baseline applies to it
```

Using `EmailStr` (already available transitively via Pydantic) is a one-line addition that satisfies
REQ-NF-05 without touching any existing endpoint's behavior — no existing endpoint is modified to add
validation it didn't have; this is scoped to the new endpoint only.

## 2. Business Rules

### 2.1 Premium Usage-Limit Table (REQ-F-06)

| Usage Item | Standard limit | Premium limit |
|---|---|---|
| Chat credits | 2,000 | 10,000 |
| Chatbots | 3 | 10 |
| Document pages | 1,000 | 5,000 |

Rule: on upgrade, update only the `limit` field of each matching entry in `billing_data[email].usages`
by name. The `used` field is never reset. The separate `on_demand_usage` balance/availability fields
are also never reset on upgrade (Q2 decision, REQ-F-06) — only `on_demand_usage.notice` changes, to
reflect that on-demand credit is now available.

### 2.2 Proration Formula (REQ-F-05, REQ-F-07)

```
days_remaining = (renew_at_date - today_date).days   # both dates, no time-of-day component
prorated_charge = round((PREMIUM_PRICE - STANDARD_PRICE) / DAYS_IN_MONTH * days_remaining, 2)
# PREMIUM_PRICE = 50, STANDARD_PRICE = 20, DAYS_IN_MONTH = 30 (fixed constants, matching the PRD)
```

This single calculation is shared, unchanged, between the `dry_run` (preview) path and the commit
path — the ONLY difference between the two paths is whether the write step (2.3) executes.

### 2.3 Guard Clauses (order matters — same order for both `dry_run` and commit)

1. `email` fails Pydantic validation (missing/malformed) -> FastAPI's automatic `422` (framework
   default, not a custom branch — matches how `LoginRequest`/`RegisterRequest` already behave).
2. `email not in users` -> `401`.
3. `users[email]["plan"] == "Premium"` -> `400 {"detail": "Already on Premium plan"}`.
4. Otherwise -> compute the proration (2.2). If `dry_run=true`, return the preview response (3.2) and
   STOP — no writes. Otherwise, apply the write step (2.4) and return the commit response (3.1).

These three guard clauses (401 unknown email, 400 already-Premium, 422 malformed body) are treated as
ONE scenario class alongside the happy path — each is a one-line check with no independent business
logic, identical in shape to the guard clauses every other endpoint in `main.py` already uses. This is
the reasoning recorded in the Step 18.6 granularity log for why Story 1.1's AC-6/AC-7 do not count as
separate scenario classes requiring their own stories.

### 2.4 Write Step (commit path only, REQ-F-05, REQ-F-06)

Applied only when the guard clauses (2.3) all pass AND `dry_run` is not `true`:

1. `users[email]["plan"] = "Premium"`; `users[email]["price"] = "$50/month"`.
2. `billing_data[email]["plan_name"] = "Premium"`; `billing_data[email]["price"] = "$50/month"`.
3. For each entry in `billing_data[email]["usages"]`, set `limit` per the table in 2.1 (matched by
   `name`); leave `used` untouched.
4. `billing_data[email]["on_demand_usage"]["notice"] = "On-demand credit is available on your Premium plan."`
   (balance/availability fields, if any, untouched — Q2 decision).
5. Compute `effective_from` = today's date (ISO format, matching `renew_at`'s existing format).

No transaction/rollback mechanism is needed — this is a single in-process dict mutation with no
partial-failure surface (no I/O between steps 1-5); if the process crashes mid-mutation, that failure
mode already exists identically in `register()`'s multi-dict write today, so this story does not
introduce a new risk class.

## 3. Data Flow / API Contract

### 3.1 Commit response (`POST /api/billing/upgrade`, no `dry_run`)

```json
{
  "success": true,
  "prorated_charge": 24.00,
  "new_plan": "Premium",
  "effective_from": "2026-09-17",
  "renew_at": "2026-10-04"
}
```

### 3.2 Dry-run response (`POST /api/billing/upgrade?dry_run=true`)

Same shape as 3.1 — the frontend confirmation panel (Story 1.1 AC-4) reads `prorated_charge` and
`renew_at` from it identically regardless of which call produced it, keeping the two paths
interchangeable from the caller's point of view except for the mutation.

## 4. Error Handling

| Condition | Response | Notes |
|---|---|---|
| Malformed/missing `email` in body | `422` | FastAPI/Pydantic default — no custom handling needed |
| Unknown `email` | `401` | Matches every existing endpoint's pattern |
| Already Premium | `400 {"detail": "Already on Premium plan"}` | Idempotency (REQ-NF-03); identical for `dry_run` and commit |
| Network/loading error on the frontend | Inline error message under the confirmation panel, panel stays open | Story 1.1 AC-11 |

No new global error-handling infrastructure is introduced — this story reuses the existing FastAPI
default exception handling (`atlas-deep-dive.md` confirms no custom error middleware exists today, and
none is required for this scope).

## 5. Frontend Component Design (`Billing.jsx`)

No new components are extracted into separate files — this story follows the existing convention
(other UI helper components like `InfoIcon`/`UsageIcon` are already defined inline in `Billing.jsx`,
per the Deep Dive's Component Catalog) and adds new inline pieces the same way:

### 5.1 State additions to the `Billing` component

```
upgradeState: "idle" | "previewing" | "confirming" | "submitting" | "error"
preview: { proratedCharge, renewAt } | null   # populated by the dry_run call
upgradeError: string | null
```

### 5.2 Interaction flow (maps directly to Story 1.1's ACs)

```
idle (Standard badge + button visible, AC-1)
  -> user clicks "Upgrade to Premium"
  -> previewing: call POST /api/billing/upgrade?dry_run=true (AC-4)
  -> confirming: panel shows price/prorated charge/renew date + Confirm/Cancel (AC-4, AC-5)
       -> Cancel -> idle, no calls made (AC-5)
       -> Confirm -> submitting: loading spinner (AC-9), call POST /api/billing/upgrade
            -> success -> re-fetch GET /api/billing, dismiss panel, badge -> Premium (AC-2, AC-10)
            -> error -> error: inline message under panel, panel stays open, user can retry (AC-11)
```

### 5.3 API integration points

- `GET /api/billing` (existing, unchanged) — supplies `plan_name` for the idle-state button/badge
  branch (AC-1/AC-2) and is re-fetched on success (AC-10).
- `POST /api/billing/upgrade?dry_run=true` (new) — preview.
- `POST /api/billing/upgrade` (new) — commit.

### 5.4 Accessibility (AC-3)

The button gets `aria-label="Upgrade to Premium plan"` and is a native `<button>` element (not a
styled `<div>`), so keyboard focus/activation (Enter/Space) is native and needs no custom key-handler
code — consistent with how the existing codebase has no custom keyboard-handling anywhere (Deep Dive
finding: no accessibility infrastructure exists today, so this story does not need to retrofit any).

---

## Design References Consulted

None — no design references were named at any stage.
