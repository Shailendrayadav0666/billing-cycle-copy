# Requirements — Self-Serve Premium Upgrade

## Intent Analysis Summary

- **User request**: "using aire and helix mcp fetch the epic and start the workflow" — build the Epic
  pulled from Atlas: *Self-Serve Premium Upgrade*.
- **Request type**: New Feature (self-serve mid-cycle plan upgrade on an existing brownfield POC).
- **Scope estimate**: Multiple Components — frontend (`src/frontend/src/pages/Billing.jsx`,
  `src/frontend/src/App.css`) and backend (`src/backend/main.py`).
- **Complexity estimate**: Moderate — single new endpoint + one UI flow, but touching the system's
  auth pattern and its only write path into shared in-memory state.
- **Sources consulted**: Epic (Atlas, doc 4039), parent PRD (Atlas, doc 3551), Atlas Deep Dive
  (`spec/plans/atlas-deep-dive.md`, exhaustive, 13/13 steps). No Context Project artifacts (user opted
  out at Workspace Detection) and no Design References named.
- **Extensions**: Resiliency Baseline = **No** (decided Requirements Analysis, Q5). Property-Based
  Testing = **No** (decided Requirements Analysis, Q6). Security Baseline and Playwright Test
  Automation remain always-mandatory per CLAUDE.md.

---

## Functional Requirements

**REQ-F-01 — Upgrade CTA on the Billing page**
Add an "Upgrade to Premium" button inside the existing `plan-row` section of `Billing.jsx`, adjacent to
`plan-card`. Visible only when `data.plan_name === 'Standard'`. When `data.plan_name === 'Premium'`,
render a `Premium` badge in that area instead (reusing the existing `standard-badge` CSS pattern),
never the button. *(PRD FR-01, AC-1, AC-2)*

**REQ-F-02 — Inline confirmation panel**
On button click, show an inline confirmation panel (no full-page modal) within the `plan-card` area,
showing: Premium price ($50/month), the prorated charge for remaining days (from the API — see
REQ-F-07), the unchanged renewal date, and **Confirm Upgrade** / **Cancel** actions. The upgrade is
never committed before the user explicitly clicks **Confirm Upgrade**. *(PRD FR-02, AC-3, AC-4)*

**REQ-F-03 — Loading, success, and error states**
Show a loading spinner on **Confirm Upgrade** while the API call is in flight. On success: re-fetch
`GET /api/billing`, dismiss the confirmation panel, and update the badge to `Premium`. On error: show
an inline error message below the confirmation panel and keep the panel open so the user can retry.
*(PRD FR-03, AC-5, AC-6)*

**REQ-F-04 — Accessibility**
The upgrade button must be keyboard-accessible and carry a descriptive `aria-label`. *(PRD FR-04)*

**REQ-F-05 — `POST /api/billing/upgrade` endpoint**
New endpoint, body `{ "email": string }`:
1. Look up `email` in the `users` dict — `401` if not found.
2. If `users[email]["plan"] == "Premium"` → `400 {"detail": "Already on Premium plan"}` (no double-charge).
3. Calculate the prorated charge: `(50 - 20) / 30 * days_remaining`, rounded to 2 decimals, where
   `days_remaining` is the number of days between today and the stored `renew_at` date.
4. Update `users[email]`: `plan` → `"Premium"`, `price` → `"$50/month"`.
5. Update `billing_data[email]`: `plan_name` → `"Premium"`, `price` → `"$50/month"`,
   `on_demand_usage.notice` → `"On-demand credit is available on your Premium plan."`, and the usage
   limits per REQ-F-06.
6. Return `{ "success": true, "prorated_charge": <float>, "new_plan": "Premium",
   "effective_from": <today>, "renew_at": <existing renew_at> }`.
*(PRD FR-05, AC-7, AC-8, AC-9)*

**REQ-F-06 — Premium usage-limit and on-demand-balance update**
On upgrade, update `billing_data[email].usages` totals: chat credits 2,000 → 10,000; chatbots 3 → 10;
document pages 1,000 → 5,000. **Used amounts carry over — never reset.** The separate on-demand
balance also **carries over as-is** (Q2 decision: it starts at whatever it currently is — effectively
0 for a Standard user, since Standard users cannot accrue on-demand usage — and becomes usable going
forward; no separate starting credit grant is issued on upgrade). *(PRD FR-06; Q2 answer: A)*

**REQ-F-07 — Proration preview via `dry_run` query parameter**
`POST /api/billing/upgrade?dry_run=true` returns the prorated charge (same calculation as REQ-F-05
step 3) **without** committing the upgrade — no writes to `users` or `billing_data`. The frontend
confirmation panel (REQ-F-02) calls this to populate the preview before the user confirms; the
follow-up commit call omits the flag. This is the SAME endpoint, not a separate route.
*(PRD FR-07; Q1 decision: A — single endpoint with `dry_run` query param, not a separate route)*

**REQ-F-08 — All existing billing data still renders correctly post-upgrade**
Usage bars, renewal date, and the on-demand card must all continue to render correctly immediately
after an upgrade — zero regressions on the existing Billing page. *(PRD AC-10)*

---

## Non-Functional Requirements

**REQ-NF-01 — Response time**
`POST /api/billing/upgrade` (both the `dry_run` preview and the commit) responds in < 200ms — in-memory
data, no external calls. *(PRD Section 7)*

**REQ-NF-02 — Auth pattern parity (deliberate scope decision)**
The new endpoint authenticates by looking up `email` in the `users` dict — the SAME pattern as the
existing 6 endpoints (no signature, no expiry, no token distinct from the raw email). **This Epic does
NOT rework authentication.** *(Q3 decision: A)*

> **Recorded exception — read before Code Review.** The Atlas Deep Dive flags this pattern as
> 🔴 Critical (SECURITY-08 access-control / SECURITY-12 credential-management, per the mandatory
> Security Baseline). The user explicitly decided (Q3) that a system-wide JWT + bcrypt overhaul is a
> separate, future initiative and out of scope for this Epic — REQ-F-05 must match the existing
> pattern exactly, not diverge from it. This is a deliberate, recorded decision, not an oversight:
> later stages (Application Design, Code Generation, Code Review) MUST NOT silently "fix" the auth
> pattern on their own initiative. **However, this decision does not pre-clear the Security Baseline's
> own gates.** Because `POST /api/billing/upgrade` is *new* code, the diff-scoped SECURITY-08/
> SECURITY-12 checks in Code Review (`common/eval-framework.md` Section 2.1) will very likely flag it
> as a genuine new finding on the changed surface (matching an existing anti-pattern in old code is not
> the same as it being "already broken" in the NEW file/lines) — the D3/J2 gates score the diff, not
> whether the pattern is novel. If that happens, it must be resolved at that gate on its own terms
> (e.g., an explicit, human-approved accepted-risk sign-off recorded in the security review, scoped
> narrowly to "matches pre-existing endpoint pattern, org-approved for this POC") rather than treated as
> a contradiction of this requirement. Flagging this now so it is not a surprise later.

**REQ-NF-03 — Idempotency and concurrency**
Calling the upgrade endpoint twice for an already-Premium user returns `400` and never double-charges
(REQ-F-05 step 2). Basic check-then-set idempotency, matching the existing code's style and rigor, is
sufficient — no explicit per-user locking or atomic compare-and-set is required for this Epic.
*(PRD Section 7; Q4 decision: A)*

**REQ-NF-04 — CORS unchanged**
No changes to the existing `allow_origins=["*"]` CORS configuration are required by this Epic.
*(PRD Section 7)*

**REQ-NF-05 — Applicable Security Baseline rules still apply to new code**
Rules not implicated by the accepted auth-pattern-parity decision (REQ-NF-02) remain fully enforced on
the code this Epic introduces: input validation on the new endpoint's body (SECURITY-05), no secrets
or PII in logs (SECURITY-03), safe/fail-closed error handling with no internal detail leakage
(SECURITY-09, SECURITY-15), and no new hardcoded credentials (SECURITY-12's credential-storage clause,
independent of the token-format exception above).

**REQ-NF-06 — Test coverage**
Unit test coverage for changed files, the behavioural (Gherkin) scenario pass rate, and the J1/J2 judge
minimums are enforced automatically per `tests/.evals/config.json` thresholds (`unitTestCoverageMin`,
`behaviorScenarioPassRateMin`, `llmJudgeArchitectureScoreMin`, `llmJudgeSecurityScoreMin`) during Code
Generation — no additional project-specific target is set by this Epic beyond the framework defaults.

---

## Out of Scope (unchanged from the Epic/PRD)

- Real payment processing (mocked/simulated charge for this POC)
- Downgrade flow (Premium → Standard)
- Email notifications
- Admin dashboard/reporting
- Cancellation flow
- Annual billing (PRD OQ-4 — flagged for a future roadmap item, not this Epic)
- System-wide authentication overhaul (JWT + bcrypt) — see REQ-NF-02's recorded exception

---

## Open Questions Resolved

| # | Question | Decision |
|---|---|---|
| PRD OQ-2 / Epic OQ-1 | `dry_run` as separate endpoint or query param? | Query param on the same endpoint (REQ-F-07) |
| PRD OQ-3 / Epic OQ-2 | On-demand balance: carry over or reset on upgrade? | Carries over as-is (REQ-F-06) |
| PRD OQ-1 | Preview shown before or after clicking the main CTA? | Before (already fixed in the PRD's own spec — REQ-F-02) |
| PRD OQ-4 / Epic OQ-3 | Annual billing? | Out of scope, unchanged |
| (new, Requirements Analysis Q3) | Auth hardening in scope for this Epic? | No — match existing pattern (REQ-NF-02) |
| (new, Requirements Analysis Q4) | Concurrency protection beyond basic idempotency? | Not required (REQ-NF-03) |

---

## Design References Consulted

None — no design references were named at Workspace Detection or during this stage.

## Context Project Artifacts Consulted

None — the user opted out of both Existing Knowledge and New References at Workspace Detection.
