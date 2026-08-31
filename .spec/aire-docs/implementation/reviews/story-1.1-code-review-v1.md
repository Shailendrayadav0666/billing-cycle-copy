# Code Review — Story 1.1 (v1)

**Story**: 1.1 — Mid-Cycle Subscription Upgrade (Standard → Premium) · `LOCAL` · 🔵 In Development
**Branch**: `story/1.1-mid-cycle-subscription-upgrade`
**Reviewer**: automated, **read-only** — this review edits no source
**AIRE**: v1.0 · **Verdict**: 🔴 **FINDINGS — remediation required**

---

## Scope

| File | Change |
|---|---|
| `src/backend/main.py` | +4 units, +2 endpoints, +4 constants, 3 store annotations, import sort |
| `src/frontend/src/pages/Billing.jsx` | dynamic plan label, CTA, modal, banner, 2 handlers |
| `src/frontend/src/App.css` | 8 new classes |
| `tests/unit/` (8 files), `tests/behavior/` (1 file) | 182 tests |
| `ruff.toml`, `mypy.ini`, `.gitleaks.toml`, `pytest.ini` | bootstrapped gate configs |

## Captured evidence cited (NOT re-executed by this review)

| Gate | Result | Artifact |
|---|---|---|
| Unit + coverage | 182 passed · **changed-surface 100% (62/62)** ≥ 90% | `unit-test-evidence/story-1.1/` |
| Behaviour B1+B2 | 25 scenarios passed | `behavior/story-1.1.feature` |
| API & contract | 16/16 on both endpoints | `api-contract-test-evidence/story-1.1/api-contract-test-run.log` |
| Regression | 182 passed · **0 new** vs baseline | `unit-test-evidence/story-1.1/full-regression.log` |
| Static D1–D7 | all PASS | `eval-evidence/story-1.1/static/post/results.json` |

---

## 🔴 Blocker

### F1 — Zone C can raise, producing a half-upgraded record (`src/backend/main.py:~330`)

`POST /api/billing/upgrade`'s Zone C is documented as containing only writes that "cannot raise",
which is the entire basis for NFR-C5 and constraint **ARCH-01** holding without a transaction. The
last line breaks that invariant:

```python
record["on_demand_usage"]["notice"] = PREMIUM_ON_DEMAND_NOTICE
```

This is a **nested subscript**. If a billing record has no `on_demand_usage` key it raises
`KeyError` — *after* the five preceding writes have already landed.

**Confirmed by execution, not inference.** A record with `on_demand_usage` removed produces:

```
status: 500
plan_name after the failed call: Premium
users plan after the failed call: Premium
PARTIAL WRITE OCCURRED: True
```

The subscriber is charged nothing extra but ends up **billed as Premium with Standard quotas and a
Standard notice** — the exact inconsistent state the three-zone discipline exists to prevent.

`users[payload.email]` in the first two writes has the same shape of risk, though it is guarded by
the Zone A 401 check so it cannot currently fail.

**Constraint violated**: ARCH-01 — *"Score 0 if any state write … is separated from the other writes
by a call that can raise."* A nested subscript on a possibly-absent key is such an operation.

**Required fix**: resolve `on_demand_usage` (and the user record) in **Zone B**, so any `KeyError`
happens before the first write. Zone C then genuinely contains only assignments on resolved objects.

**Severity rationale**: 🔴 rather than 🟠 because it is money-adjacent, it violates a Section 10
constraint that gates the story, and it silently corrupts billing state rather than failing cleanly.

---

## 🔵 Nits

### F2 — Duplicated fetch logic (`Billing.jsx`)

`loadBilling()` is defined and then the mount `useEffect` re-implements the same fetch inline instead
of calling it. Harmless, but two copies of one call will drift. *Fix: call `loadBilling()` from the
effect.*

### F3 — `success` state is never cleared

Once set, the banner persists for the page's lifetime. Correct in practice (a subscriber can upgrade
only once, enforced by the 409 guard), so this is an observation rather than a defect. No change
required.

---

## ✅ Verified correct

- **ARCH-02** — no request model exposes a monetary field; `grep` finds no `*`, `/`, `+`, `-` applied to a price or quota anywhere in `Billing.jsx`. Only `.toFixed(2)` formatting.
- **ARCH-03** — `billing_data.get(email)` with **no fallback argument**; a missing record raises 404. The `billing_data.get(email, billing_data["tpg@example.com"])` pattern is not reproduced. Test `test_a_caller_with_no_billing_record_gets_404_not_another_users_data` pins it.
- **ARCH-04** — exactly one `_resolve_upgrade_context` definition, two call sites, no re-implemented guard or formula in either handler.
- **ARCH-05** — `requirements.txt` and `package.json` have **zero added lines**. The only new imports are `typing.Any` (stdlib) and `fastapi.responses.JSONResponse` (already-present dependency).
- **ARCH-06** — no logging call and no `print` in any of the five new units; asserted by `test_the_new_backend_code_contains_no_logging_at_all`.
- **Guard order** 401 → 404 → 409 correct; `test_the_guard_order_does_not_leak_existence_before_authentication` proves an unauthenticated caller learns nothing.
- **`renew_at` preserved by omission** — no assignment to it exists in either store.
- **Quota merge** preserves `id`, `label` and `used`; unknown ids pass through; input list not mutated.
- **402 body** is the exact two-key shape via `JSONResponse`, as the design predicted `HTTPException` could not produce.
- **Scope discipline** — F-3, F-5 and F-6 left untouched as recorded; the six pre-existing endpoints unmodified.

---

## 🔒 Security Baseline — diff-scoped review

Only the changed surface. The 16 SECURITY-NN rules; irrelevant ones marked N/A rather than silently skipped.

| Rule | Verdict |
|---|---|
| Encryption at rest / in transit | N/A — no new secret or persisted datum |
| Logging & redaction | ✅ no logging exists in the new code (ARCH-06) |
| Security headers | N/A — no header change |
| Input validation | ✅ Pydantic-typed body; `email` never interpolated into a sink |
| SSRF | N/A — no outbound request; the gateway is an in-process pure function |
| File upload | N/A |
| **Access control** | ✅ 401 first; caller-scoped lookups only; **no cross-email read or write** (ARCH-03) |
| CSRF | N/A — no cookie-based session introduced |
| JWT | N/A — auth unchanged |
| Network config | N/A |
| Credential management | ✅ no card data, token or secret accepted, stored or emitted |
| Session integrity | N/A |
| Supply chain | ✅ zero new dependencies |
| XML / XXE | N/A — JSON only |
| Alerting | N/A — none exists in this system |
| **Error handling** | ✅ four fixed-literal bodies, zero interpolation; leak assertions in tests |

**New Security Baseline violations on the changed surface: 0.** No `SEC-ISS-XXX` raised.
Pre-existing findings (email-as-token, plain-text passwords, wildcard CORS, token in query params,
unpinned deps) are unchanged and out of scope — **none widened**, satisfying NFR-S7.

---

## ⚖️ Judge gates

### J1 — Architectural alignment (`architecture-rubric.json` v1.0.0)

| Criterion | Weight | Score | Note |
|---|---|---|---|
| ARCH-01 charge before write, single write site | 0.28 | **0.00** | **Finding F1** — Zone C contains an operation that can raise, between writes |
| ARCH-02 server-side pricing only | 0.22 | 1.00 | |
| ARCH-03 caller-scoped data access | 0.18 | 1.00 | |
| ARCH-04 one guard + formula implementation | 0.14 | 1.00 | |
| ARCH-05 no new runtime dependency | 0.10 | 1.00 | |
| ARCH-06 no secrets/PII in logs or errors | 0.08 | 1.00 | |

**J1 = 0.72** · threshold `llmJudgeArchitectureScoreMin` **0.85** → 🔴 **FAIL (blocking)**

### J2 — Security (`security-rubric.json` v1.0.0)

| Criterion | Weight | Score |
|---|---|---|
| SEC-A01 broken access control | 0.25 | 1.00 |
| SEC-A04 insecure design / business-logic integrity | 0.20 | 1.00 |
| SEC-A03 injection & input validation | 0.15 | 1.00 |
| SEC-A09 logging failures / sensitive exposure | 0.12 | 1.00 |
| SEC-A05 misconfiguration | 0.10 | 1.00 |
| SEC-A07 authentication failures | 0.10 | 1.00 |
| SEC-A02 cryptographic failures | 0.05 | 1.00 |
| SEC-A06 vulnerable components | 0.03 | 1.00 |

**J2 = 1.00** · threshold `llmJudgeSecurityScoreMin` **0.85** → ✅ **PASS**

*(A08 and A10 are `notApplicable` in the rubric and excluded from the weighting, as designed.)*

---

## Verdict

🔴 **1 Blocker, 0 Issues, 2 Nits.** J1 fails at 0.72 against a 0.85 threshold.

Routing automatically to **Remediate (SH-LOOP-5)** — no user decision. F1 must be fixed, F2 applied
as a cheap cleanup, F3 needs no change. Then the gate re-runs.
