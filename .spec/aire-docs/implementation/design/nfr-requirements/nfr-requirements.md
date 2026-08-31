# NFR Requirements — EPIC-1 Mid-Cycle Subscription Upgrade

**Depth**: **Minimal** — per the execution plan. The tech stack is fixed and no new dependency is
permitted (NFR-1), so this stage **consolidates and sharpens** what `requirements.md` already holds
rather than discovering new NFRs. Its purpose is to be a clean input to NFR Design and to the
`architecture.md` Section 10 constraints that mechanically derive the blocking J1 rubric.

**Inputs**: `design/functional-design/*` (all four) · `planning/requirements/requirements.md` ·
`planning/user-stories/stories.md` · `planning/reverse-engineering/knowledge-graph.md`

---

## 1. Scope posture — what "NFR" means for a POC

Atlas doc 3155 rates this system as a deliberately compact POC with **four critical pre-existing
security findings** and **zero tests**. Two honest consequences:

1. **Production-grade NFRs are not achievable in this cycle and are not attempted.** There is no
   database, no real auth, no CI for the application. Writing an availability or throughput target
   here would be fiction.
2. **The NFRs that *are* in force are the ones this change can actually honour** — correctness of the
   money path, isolation of the caller's record, no new dependency, and testability. Those are
   enforced as blocking.

Pre-existing baseline violations elsewhere in the system are **recorded, not fixed** (Section 6).

---

## 2. Correctness NFRs *(blocking — the money path)*

| ID | Requirement | Verification | Source |
|---|---|---|---|
| **NFR-C1** | `prorated_charge == round((40.0 - 20.0) / 30 * days_remaining, 2)` for every integer `days_remaining` in 1..30. | Unit test over the full 30-value domain — exhaustive, not sampled. | NFR-3, BR-2, D-1 |
| **NFR-C2** | `days_remaining >= 1` always, including a cycle ending today or already past. | Unit test at and past the boundary. | BR-2 |
| **NFR-C3** | `0.67 <= prorated_charge <= 20.00`. | Asserted as an invariant, never as a literal expected amount. | NFR-4 |
| **NFR-C4** | No test asserts a hardcoded dollar amount derived from a fixed `renew_at`. | Static check on the test sources — `renew_at` is dynamic (F-1). | NFR-4 |
| **NFR-C5** | After a 402, every field of `users[email]` and `billing_data[email]` is byte-identical to its pre-request value. | Deep-compare a snapshot taken before the request. | NFR-5, AC-25 |
| **NFR-C6** | `renew_at` is identical before and after a successful upgrade, in **both** dicts. | Assert both, separately. | FR-11, AC-23, BR-7 |
| **NFR-C7** | `used` is preserved for every usage entry across an upgrade; only `total` (and the `documents-pages` help text) changes. | Compare entry-by-entry on `id`. | FR-13, AC-21, D-3 |

**NFR-C5 and NFR-C7 exist because the Epic's own design would have violated them** — its
`PREMIUM_QUOTAS` list would have reset `used` to 0. They are the two NFRs most worth having a machine
check.

---

## 3. Security NFRs *(blocking — Security Baseline, diff-scoped)*

Restated from `requirements.md` SEC-1..SEC-6, now bound to concrete verification.

| ID | Requirement | Verification | Source |
|---|---|---|---|
| **NFR-S1** | Both new endpoints return 401 when `email not in users`, before any other check. | Test each endpoint unauthenticated. | SEC-1, BR-8 |
| **NFR-S2** | Neither new endpoint reads or writes a record for an email other than the caller's. The `billing_data.get(email, billing_data["tpg@example.com"])` fallback is **absent** from the new code. | Static check for the fallback pattern + a test that a user with no billing record gets 404, not the seed user's data. | SEC-2, F-3, AC-9 |
| **NFR-S3** | `UpgradeRequest` declares exactly one field, `email: str`. No amount, plan, or card field exists on any request model. | Static check on the model definition. | SEC-3, SEC-6, AC-18 |
| **NFR-S4** | No email, amount, card value, or secret is written to any log, stdout, or exception message. `charge_card` performs no I/O. | Static check: no logging call and no `print` in the new code. | SEC-4, AC-17 |
| **NFR-S5** | Error bodies are fixed literals. No stack trace, dict content, or other user's data appears in a 401/402/404/409 response. | Assert exact response bodies. | SEC-5, AC-26, BR-10 |
| **NFR-S6** | The charged amount is computed server-side on every call and is not readable from, or influenced by, the request. | Test that an extra `amount` field in the body is ignored and the server-computed value is charged. | SEC-6, AC-18 |
| **NFR-S7** | The change introduces **no new** Security Baseline violation on the changed surface, and does not widen an existing one. | Diff-scoped automated security review (`agents/code-security-review-agent.md` Phase 2.5). | Security Baseline extension |

---

## 4. Maintainability and testability NFRs

| ID | Requirement | Verification | Source |
|---|---|---|---|
| **NFR-M1** | **No new runtime dependency**, frontend or backend. `requirements.txt` and `package.json` are unchanged. | Diff check on both manifests. | NFR-1 |
| **NFR-M2** | Unit test coverage on the changed surface meets `unitTestCoverageMin` from `.evals/config.json`. | Coverage gate. | NFR-6 |
| **NFR-M3** | The 401/404/409 guard chain and the proration computation exist in exactly **one** place, shared by both endpoints. | Static check: one `_resolve_upgrade_context` definition, two call sites. | D-2, business-logic-model.md |
| **NFR-M4** | `charge_card` and `_premium_usages` are **pure** — no I/O, no clock, no randomness, no mutation of their arguments. | Unit-testable without any fixture; `_premium_usages` asserted not to mutate its input. | BR-9, D-2 |
| **NFR-M5** | No existing endpoint, model, or CSS class is modified beyond what an AC requires. Full regression green against the captured baseline. | Regression gate vs baseline. | epic-level AC |
| **NFR-M6** | The UI-relevant acceptance criteria are automatable in a browser. | Playwright extension, after both PRs merge. | NFR-7 |

---

## 5. Performance and scalability — deliberately minimal

| ID | Requirement | Rationale |
|---|---|---|
| **NFR-P1** | Both endpoints are O(1) plus O(n) over the caller's usage list, where n = 3. No loop over `users` or `billing_data`, and no nested scan. | The existing endpoints are all direct `dict.get(email)` lookups; the new ones match that shape. |
| **NFR-P2** | `charge_card` performs no network call, so neither endpoint has an external-latency component. | BR-9, AC-17 |

**No throughput, latency-percentile, or availability target is set.** Stating one would be
unverifiable: the app is a single uvicorn process with an in-memory store that loses all data on
restart, and there is no load harness. Scalability is structurally capped by the in-memory store —
already documented by Atlas as a critical architectural finding, and out of scope here.

---

## 6. Pre-existing baseline findings — recorded, explicitly NOT in scope

From Atlas doc 3155, all pre-dating this cycle. The Epic's own acceptance criteria forbid touching
auth, so fixing these is a separate cycle.

| # | Finding | Atlas severity |
|---|---|---|
| 1 | Email used as the auth token — trivially forgeable, no expiry | 🔴 Critical |
| 2 | Passwords stored and compared in plain text | 🔴 Critical |
| 3 | No persistence — all data lost on restart | 🔴 Critical |
| 4 | `allow_origins=["*"]` with `allow_credentials=True` — a CORS spec violation | 🔴 Critical |
| 5 | Zero test coverage across all modules | 🔴 Critical |
| 6 | Auth token transported in query parameters — leaks into logs, history, proxies | 🟡 High |
| 7 | Backend dependencies entirely unpinned | 🟡 High |

**NFR-S7 is the guard**: this change must not make any of these worse, and must not add a new one.
Note that finding 5 is *partially* improved by this cycle — it introduces the repo's first tests, on
the changed surface only.

---

## 7. Where these NFRs are enforced

| NFR group | Enforced by |
|---|---|
| NFR-C1..C7 | Unit tests + the Gherkin behaviour spec (B1/B2/B3) |
| NFR-S1..S6 | Unit/API tests + static checks |
| NFR-S7 | Diff-scoped automated security review inside Code Review |
| NFR-M1, M3, M4 | Static D1–D7 gates |
| NFR-M2 | Coverage gate |
| NFR-M5 | Full regression vs the captured baseline |
| NFR-M6 | `/playwright-implement`, post-merge |
| NFR-C5, NFR-S2, NFR-S3, NFR-M1 | **Candidates for `architecture.md` Section 10 verifiable constraints** — each names something that scores 0 in a diff, so each can fairly drive the blocking J1 gate |
