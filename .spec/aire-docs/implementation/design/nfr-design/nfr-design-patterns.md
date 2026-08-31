# NFR Design Patterns — EPIC-1 Mid-Cycle Subscription Upgrade

**Depth**: **Minimal** — per the execution plan. This stage answers **how** each blocking NFR is
actually realised in code, rather than restating that it must be. Every pattern below is a concrete
structural choice with the NFR it satisfies and how it is verified.

**Inputs**: `design/nfr-requirements/` (both artifacts) · `design/functional-design/` (D-1..D-3, BR-1..BR-10)

---

## 1. The governing idea — make NFRs structural, not procedural

A procedural NFR ("remember not to write before charging") is honoured by discipline and broken by
the next edit. A structural NFR ("the write site is unreachable from the declined branch") is honoured
by the shape of the code and *cannot* be broken without visibly rewriting that shape.

Every pattern here is chosen so the NFR holds **by construction**, which is also what makes it
mechanically checkable in a diff — the property the `architecture.md` Section 10 constraints need.

---

## 2. Pattern P-1 — Guard-Then-Compute Gateway *(satisfies NFR-C1, NFR-M3, NFR-S1, NFR-S2, NFR-S5)*

**Problem.** Two endpoints share an identical 401 → 404 → 409 guard chain and an identical proration
computation. If those drift, the preview quotes a price the upgrade refuses to honour — a defect the
user experiences as being lied to about money.

**Pattern.** One private function is the *only* implementation of both:

```
_resolve_upgrade_context(email) -> (record, days_remaining, prorated_charge)
    raises 401 | 404 | 409
```

Both handlers' first statement is a call to it. Neither re-implements a guard or the formula.

**Structural guarantee**: divergence requires someone to add a second guard chain, which is visible in
a diff as new conditional logic in a handler.

**Verification**: static check — exactly one `def _resolve_upgrade_context`, exactly two call sites, no
`HTTPException(status_code=401|404|409` outside that function.

### Guard ordering is load-bearing

| Order | Check | Why it must be here |
|---|---|---|
| 1 | `email not in users` → **401** | An unauthenticated caller must not learn whether an email exists, has a billing record, or is Premium. Any other order leaks that. |
| 2 | no `billing_data` entry → **404** | A Premium user with no billing record is a data inconsistency, not an eligibility answer. 404 before 409. |
| 3 | `plan_name != "Standard"` → **409** | Eligibility, once identity and data are established. |

---

## 3. Pattern P-2 — Charge-Before-Write with a Single Write Site *(satisfies NFR-C5, NFR-C6, NFR-C7)*

**Problem.** NFR-C5 requires that after a 402, *no field* of two separate dicts differs. There is no
transaction, no rollback, and no persistence layer to lean on.

**Pattern.** Three ordered zones inside `POST /api/billing/upgrade`, with a hard rule about what may
appear in each:

```
ZONE A — READ + VALIDATE + COMPUTE     may raise freely; writes nothing
    _resolve_upgrade_context(...)      -> 401 / 404 / 409
    charge_card(email, amount)         -> pure, no I/O
    if declined: raise 402             <-- returns from Zone A. Zone C never runs.

ZONE B — BUILD                          may raise freely; writes nothing
    new_usages = _premium_usages(...)   pure; returns a NEW list
    plan_label = PLANS["Premium"]["label"]

ZONE C — ASSIGN                         cannot raise; the ONLY writes in the function
    6 plain dict assignments on already-resolved values
```

**Structural guarantees**:
- The 402 raise sits in Zone A, so **no assignment is reachable** from the declined path. NFR-C5 holds without a rollback because there is nothing to roll back.
- Zone C contains only `dict[key] = value` on values computed in A and B. No call, no arithmetic, no parse, no `await`. Nothing in it *can* raise, so a partial write is not merely unlikely — it is impossible.
- The handler is `def`, not `async def`, so it runs to completion on the worker thread without an interleaving point. No concurrent request observes Zone C mid-flight.
- **`renew_at` is preserved by omission** — it is never assigned in Zone C. NFR-C6 holds because the code has no line that could break it. Stronger than re-assigning the same value, which a later edit could "simplify" into recomputing it.

**Verification**: NFR-C5 by deep-comparing a pre-request snapshot after a 402; NFR-C6 by asserting both `renew_at` copies; a static check that no assignment to `users[...]` or `billing_data[...]` appears before the `charge_card` call.

---

## 4. Pattern P-3 — Pure Transform for State Change *(satisfies NFR-C7, NFR-M4)*

**Problem.** The quota merge must raise ceilings while preserving `used` and `label` (AC-21), and must
not corrupt the existing list if it fails halfway.

**Pattern.** `_premium_usages(existing) -> list[dict]` is a pure function returning a **new** list
built with `{**entry, "total": ...}`. It never mutates `existing`.

**Structural guarantees**:
- Because it returns rather than mutates, calling it in Zone B is safe: a failure leaves stored state untouched.
- Because it spreads the existing entry, `id`, `label` and `used` are carried forward **by default**. Preserving them is the fallthrough behaviour, not an extra step someone must remember. This is the direct structural answer to the Epic's `used: 0` defect (D-3).
- An entry whose `id` is absent from `PREMIUM_QUOTA_TOTALS` is returned unchanged, so a future metric is not silently dropped by an upgrade.

**Verification**: unit-test with no fixture at all; assert the input list object is unchanged after the call; assert `used` and `label` per entry by `id`.

---

## 5. Pattern P-4 — Absence of Capability *(satisfies NFR-S3, NFR-S4, NFR-S6, NFR-M1)*

**Problem.** Several security NFRs are about what the system must be **unable** to do. A validation
check can be bypassed or removed; a capability that does not exist cannot be.

**Pattern.** Realise each as a missing thing rather than a present check:

| NFR | Not this | But this |
|---|---|---|
| NFR-S3 / S6 — client cannot set the price | Validate and reject a client-supplied `amount` | `UpgradeRequest` has **one field**, `email: str`. Pydantic ignores unknown keys by default, so an `amount` in the body never reaches the handler. There is no variable to misuse. |
| NFR-S4 — no credential or amount reaches a log | Scrub log output | The new code contains **no logging call and no `print`**. `charge_card` performs no I/O of any kind. |
| NFR-S4 — no card data is handled | Encrypt card data | The gateway signature accepts only `(email, amount)`. There is no card parameter, so no card value can be stored, logged, or leaked. |
| NFR-M1 — no new runtime dependency | Review the manifests | Nothing is imported that is not already imported. `requirements.txt` and `package.json` are byte-identical in the diff. |

**Verification**: static checks — one field on `UpgradeRequest`; zero logging/`print` calls in the new
code; zero-line diff on both dependency manifests. All four are trivially checkable in a diff, which
is why NFR-S2, NFR-S3 and NFR-M1 were nominated as Section 10 constraints.

---

## 6. Pattern P-5 — Fixed-Literal Error Envelope *(satisfies NFR-S5)*

**Problem.** An error body is the easiest place for internal state to escape.

**Pattern.** Every error response is a **fixed literal** chosen at design time. No f-string, no
interpolation of any runtime value, no exception text, into any of the four bodies:

| Status | Body | Interpolated values |
|---|---|---|
| 401 | `{"detail": "Not authenticated"}` | none |
| 404 | `{"detail": "billing_record_not_found"}` | none |
| 409 | `{"detail": "already_premium"}` | none |
| 402 | `{"detail": "card_declined", "message": "Your card was declined."}` | none |

**Design note carried from Functional Design**: FastAPI's `HTTPException(detail=...)` serialises to a
single `detail` key, so it cannot produce the 402's two-key body without nesting. The 402 is returned
as a `JSONResponse` with an explicit `content` dict. Settled in design rather than discovered at the
contract gate.

**Verification**: assert exact response bodies; static check that no f-string appears in an error
response construction.

---

## 7. Pattern P-6 — Server-Recomputation over Client Round-Trip *(satisfies NFR-S6)*

**Problem.** The preview returns an amount, then the client confirms. The obvious implementation
passes the quoted amount back — and hands the client control of the price.

**Pattern.** `POST /api/billing/upgrade` **recomputes** the charge from stored state via P-1. The
preview response is never echoed back by the client, and there is nowhere in the request model to put
it (P-4).

**Accepted consequence, recorded**: if a day boundary is crossed between opening the modal and
confirming, the charged amount differs from the quoted one by one day's delta ($0.67). This is
**correct** — the subscriber pays for the days that actually remain when the money moves. Noting it so
it is not later mistaken for a bug.

**Verification**: NFR-S6 test sends a body containing an `amount` field and asserts the
server-computed value was charged.

---

## 8. Pattern P-7 — Fail-Visible Frontend Requests *(satisfies FR-10, and NFR-M5 for the new surface)*

**Problem.** The existing page uses `.then().then()` with no `.catch()`, so a failure leaves
"Loading billing..." on screen forever (finding F-5). The new flow must not add more of that.

**Pattern.** Every new call is `async/await` in `try/catch/finally`:

- `catch` always sets a user-visible message — no silent swallow on any path
- `finally` always clears `loading`, so no path leaves a spinner stuck or Confirm permanently disabled
- `res.ok` is checked before parsing, and the 402 body's own `message` is preferred so the gateway's wording reaches the user
- **Cancel stays enabled during a request**, so a hung call cannot trap the user in the modal — AC-31 requires cancel to work after a failure

**Scope boundary, flagged**: the *existing* fetch at `Billing.jsx:105-107` is deliberately untouched
(F-5, out of scope), so the file will temporarily hold both patterns. Recorded here so a reviewer
reads that as a scope boundary rather than an inconsistency.

---

## 9. NFR-to-pattern coverage

| NFR | Pattern(s) | Structural or procedural |
|---|---|---|
| NFR-C1 formula correctness | P-1 | Structural (one implementation) |
| NFR-C2, C3, C4 invariants | — | Procedural (test-authoring discipline) |
| NFR-C5 nothing mutated on 402 | **P-2** | **Structural** (write site unreachable) |
| NFR-C6 `renew_at` preserved | **P-2** | **Structural** (preserved by omission) |
| NFR-C7 `used` preserved | **P-3** | **Structural** (spread carries it by default) |
| NFR-S1 401 first | P-1 | Structural (ordered guard chain) |
| NFR-S2 no cross-email access | P-1 | Structural (single lookup by caller email) |
| NFR-S3 no client-set price | **P-4** | **Structural** (field does not exist) |
| NFR-S4 no logging of secrets | **P-4** | **Structural** (no logging call exists) |
| NFR-S5 fixed error bodies | P-5 | Structural (no interpolation) |
| NFR-S6 server recomputation | **P-4 + P-6** | **Structural** |
| NFR-S7 no new baseline violation | all | Verified by the diff-scoped security review |
| NFR-M1 no new dependency | **P-4** | **Structural** (zero-line manifest diff) |
| NFR-M2 coverage | — | Procedural (gate threshold) |
| NFR-M3 single guard implementation | P-1 | Structural |
| NFR-M4 pure helpers | **P-3** | **Structural** |
| NFR-M5 no regression | P-7 + scope discipline | Verified by the regression gate |
| NFR-P1, P2 complexity | P-1, P-3 | Structural (no scan over any store) |

**11 of 18 NFRs hold structurally.** The remainder are test-authoring or gate-threshold concerns,
which cannot be made structural and are correctly left to the gates.
