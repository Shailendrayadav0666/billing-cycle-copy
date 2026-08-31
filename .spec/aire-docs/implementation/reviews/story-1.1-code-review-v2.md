# Code Review — Story 1.1 (v2, after remediation)

**Story**: 1.1 — Mid-Cycle Subscription Upgrade (Standard → Premium) · `LOCAL` · 🔵 In Development
**Branch**: `story/1.1-mid-cycle-subscription-upgrade`
**Reviewer**: automated, **read-only**
**Remediation round**: SH-LOOP-5 round **1 of 3**
**AIRE**: v1.0 · **Verdict**: ✅ **CLEAN — zero 🔴, zero 🟠**

---

## Disposition of v1 findings

| # | Severity | Status | What changed |
|---|---|---|---|
| **F1** | 🔴 Blocker | ✅ **FIXED** | `users[payload.email]` and `record["on_demand_usage"]` are now resolved in **Zone B**. Zone C contains six plain assignments on already-resolved objects, none of which can raise. |
| **F2** | 🔵 Nit | ✅ **Addressed, differently than suggested** | See the note below — the suggested fix was rejected on principle. |
| **F3** | 🔵 Nit | ✅ **No change, as recommended** | `success` persisting is correct; the 409 guard makes a second upgrade impossible. |

### F1 — verified by execution, not by inspection

The same probe that found the defect was re-run against the fixed code:

| | Before (v1) | After (v2) |
|---|---|---|
| status | 500 | 500 |
| `plan_name` after the failed call | **`Premium`** | `Standard` |
| `users[...]["plan"]` after | **`Premium`** | `Standard` |
| billing record byte-identical | — | **`True`** |
| user record byte-identical | — | **`True`** |
| **partial write occurred** | **`True`** | **`False`** |

A malformed record still fails the request, which is correct — but it now fails **without mutating
anything**. Pinned by two new regression tests
(`test_a_malformed_billing_record_does_not_produce_a_partial_upgrade`,
`test_a_billing_record_without_usages_does_not_produce_a_partial_upgrade`), so it cannot silently
return.

### F2 — the obvious fix was rejected, and here is why

The v1 review suggested calling `loadBilling()` from the mount effect. Doing that makes
`loadBilling` a dependency of the effect, and because it is redefined on every render, the honest
dependency list becomes unstable. The only way to keep `[token]` would be a
`// eslint-disable-next-line react-hooks/exhaustive-deps` suppression.

**That was written and then removed.** SH-6 explicitly forbids suppressions as a way to satisfy a
check, and a lint suppression added to tidy a nit is exactly the shortcut the rule exists to stop.
Instead the effect keeps its own direct fetch — with a `.catch()` added, which is a genuine
improvement over the pre-existing pattern — and its dependency list stays truthfully `[token]`.
Recorded here so the "duplication" reads as a deliberate trade rather than an unaddressed nit.

---

## Gate evidence cited (NOT re-executed by this review)

| Gate | Loop | Result | Attempts used |
|---|---|---|---|
| Unit + coverage | SH-LOOP-1 | **184 passed** · changed-surface **100% (62/62)** ≥ 90% | 1 of 3 |
| Behaviour B1+B2 | SH-LOOP-7 | **25 scenarios passed** | 1 of 3 |
| Behaviour B3 | SH-LOOP-8 | **N/A** — `.spec/behavior.feature` is deliberately scenario-free (one work unit) | — |
| API & contract | SH-LOOP-2 | **16/16** on both endpoints | 1 of 3 |
| Full regression | SH-LOOP-3 | **184 passed · 0 NEW** vs baseline | 0 of 3 |
| Static D1–D7 | SH-LOOP-4 | **all PASS** | 2 of 3 |
| Judge J1/J2 | SH-LOOP-6 | see below | 1 of 3 |
| Remediate | SH-LOOP-5 | clean after round 1 | 1 of 3 |

**No loop was exhausted. No gate was skipped, weakened, or carried forward.**

---

## ⚖️ Judge gates — recomputed

### J1 — Architectural alignment (`architecture-rubric.json` v1.0.0)

| Criterion | Weight | v1 | v2 | Note |
|---|---|---|---|---|
| ARCH-01 charge before write, single write site | 0.28 | 0.00 | **1.00** | Zone C now provably cannot raise; verified by execution |
| ARCH-02 server-side pricing only | 0.22 | 1.00 | 1.00 | No monetary request field; no pricing arithmetic in any changed frontend file |
| ARCH-03 caller-scoped data access | 0.18 | 1.00 | 1.00 | `.get(email)` with no fallback; 404 on a missing record |
| ARCH-04 one guard + formula implementation | 0.14 | 1.00 | 1.00 | One definition, two call sites |
| ARCH-05 no new runtime dependency | 0.10 | 1.00 | 1.00 | Zero added manifest lines; only `typing` (stdlib) and an already-present FastAPI symbol |
| ARCH-06 no secrets/PII in logs or errors | 0.08 | 1.00 | 1.00 | No logging call exists in any new unit |

**J1 = 1.00** · threshold **0.85** → ✅ **PASS** *(was 0.72 — FAIL)*

### J2 — Security (`security-rubric.json` v1.0.0)

**J2 = 1.00** · threshold **0.85** → ✅ **PASS** (unchanged from v1; all 8 applicable criteria 1.00)

---

## 🔒 Security Baseline — diff-scoped, re-run

**New violations on the changed surface: 0.** No `SEC-ISS-XXX` raised. The five pre-existing
critical/high findings are unchanged and **none widened**, satisfying NFR-S7.

Worth noting the F1 fix *improved* the security posture: a partial write that leaves a subscriber
billed as Premium with Standard entitlements is a business-logic integrity defect
(OWASP A04), and it is now impossible.

---

## Acceptance-criteria coverage

| ACs | Verified by |
|---|---|
| AC-1..AC-4 | `data.plan_name` rendered; strict-equality CTA; behaviour Scenario Outline |
| AC-5..AC-11 | 12 preview tests + 5 behaviour scenarios |
| AC-12..AC-15 | `UpgradeModal` structure reviewed statically; **no pricing arithmetic** confirmed by grep. Browser-level assertions come from `/playwright-implement` post-merge (NFR-M6) |
| AC-16..AC-18 | 9 gateway tests + 8 price-injection tests + 5 behaviour scenarios |
| AC-19..AC-23 | 13 execute tests + 5 behaviour scenarios |
| AC-24..AC-26 | 12 declined tests + 3 behaviour scenarios |
| AC-27..AC-31 | Handler logic reviewed; 2 behaviour scenarios; browser assertions post-merge |

⚠️ **Stated plainly rather than glossed**: **AC-12, AC-13, AC-14, AC-15, AC-29 and AC-30 are
frontend-presentation criteria that no API-level test can prove.** The feature file deliberately
carries no tag for them — inventing one would have claimed coverage that does not exist. They are
verified here by static review, and their executable verification arrives with the mandatory
Playwright extension after both PRs merge. 25 of 31 ACs have executable behaviour coverage today.

---

## Verdict

✅ **CLEAN.** Zero 🔴, zero 🟠, all nits dispositioned. J1 1.00, J2 1.00, both above threshold.

Proceeding automatically to commit, push and PR.
