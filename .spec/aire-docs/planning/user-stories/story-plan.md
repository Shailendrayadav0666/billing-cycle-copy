# User Stories — Story Plan (Part 1)

**Epic**: EPIC-1 — Mid-Cycle Subscription Upgrade (Standard → Premium)
**Tracker**: LOCAL
**team_size**: 2 (fixed framework default — NOT asked)
**story_creation_mode**: all-at-once (fixed framework default — NOT asked)
**Created**: 2026-08-31

> This plan is **announced, not approved**. The approval gate is **GATE 1**, on the generated story
> set (Part 2).

---

## 1. Inputs

- [x] `planning/requirements/epic-brief.md` — Atlas doc 3157, 5 proposed stories
- [x] `planning/requirements/requirements.md` — FR-1..FR-13, NFR-1..NFR-7, SEC-1..SEC-6
- [x] `planning/reverse-engineering/knowledge-graph.md` — Atlas doc 3155, existing architecture
- [x] `## Context References` in `aire-state.md` → **No** (user declined). No wireframes or API specs to load.

---

## 2. Story Slicing Analysis (Step 1.5 — SPIDR applied per capability)

The Epic proposes **5** stories. Three of them breach the hard sizing ceilings, so SPIDR splits them.

| Epic story | Ceiling breach | SPIDR axis used | Splits into |
|---|---|---|---|
| **1** — Upgrade CTA + dynamic badge | Title needs "and"; two distinct rules | **R** (Rules) | (a) render the real plan; (b) show the CTA only when Standard |
| **2** — Preview endpoint + modal | **Two architectural layers newly** (new backend endpoint AND new frontend modal) | **I** (Interfaces) | (a) `GET /api/billing/upgrade-preview` + proration; (b) confirmation modal |
| **3** — Execute upgrade + dummy payment | **Two layers**, and mixes happy path with failure path — two scenario classes | **I** + **P** (Paths) | (a) `POST /api/billing/upgrade` happy path; (b) declined path → 402 with zero mutation; (c) frontend success handling; (d) frontend failure handling |
| **4** — Premium quotas & billing data | Would push the happy-path endpoint story past 5 ACs | **D** (Data) | Stays its own story — the Premium quota/notice data variation |
| **5** — Already-Premium guard | Mixes a backend rule with a frontend condition; the frontend half duplicates story 1(b) | **R** | Backend 409 rule only; the "no CTA when Premium" half is an AC of 1(b) |

**Deliberately NOT split**: `charge_card()` is pure plumbing with no observable value on its own. Per
the INVEST caveat on Step 1.5, it is folded into the happy-path upgrade story rather than stranded as
a plumbing story.

### Resulting candidate story set (10)

| # | Story | Layer | Scenario class |
|---|---|---|---|
| 1.1 | Billing page renders the real plan name, price and badge | Frontend | Happy |
| 1.2 | "Upgrade to Premium" CTA shown only to Standard subscribers | Frontend | Rule |
| 1.3 | `GET /api/billing/upgrade-preview` returns the prorated quote | Backend | Happy |
| 1.4 | Already-Premium guard — 409 on both upgrade endpoints | Backend | Rule / edge |
| 1.5 | Proration confirmation modal | Frontend | Happy |
| 1.6 | `POST /api/billing/upgrade` — charge and flip to Premium | Backend | Happy |
| 1.7 | Premium quotas and on-demand notice applied on upgrade | Backend | Data |
| 1.8 | `POST /api/billing/upgrade` — card declined returns 402, mutates nothing | Backend | Failure |
| 1.9 | Upgrade success — refresh, banner, CTA removed | Frontend | Happy |
| 1.10 | Upgrade failure — inline error, modal stays open | Frontend | Failure |

Every candidate passes the ceilings: ≤ 5 ACs · one architectural layer newly · no "and"/"or" in the title · one scenario class.

**Parallelism**: 1.1, 1.3 and 1.5's prerequisites make at least 3 stories startable immediately — comfortably above `team_size` = 2.

---

## 3. Question for the user

```
❓ How many user stories should I create for this work?

   💡 Recommended: 10 stories  (suggested range: 8–10)

   Why 10:
   - The Epic's own 5 stories breach the Step 1.5 hard sizing ceilings: its Story 2 and
     Story 3 each span two architectural layers newly (new backend endpoint AND new
     frontend UI), and Story 3 additionally mixes the happy path with the card-declined
     failure path — two scenario classes in one story.
   - SPIDR-slicing on Interfaces (backend vs frontend), Paths (success vs declined) and
     Rules (the already-Premium guard, the CTA eligibility condition) yields 10
     single-purpose stories, each with ≤5 acceptance criteria and one thing to verify.
   - Leaves at least 3 stories startable immediately, above team_size = 2, so neither
     developer is idle.

   Trade-off, stated plainly: 10 stories means 10 branches, 10 PRs and 10 ve test plans
   for roughly 3.5 days of work. If you would rather trade review granularity for less
   process overhead, 8 is the sensible floor — it merges the two frontend
   success/failure stories into their parent stories (1.9+1.10 into 1.5, and 1.7 into
   1.6), at the cost of two stories carrying 6 ACs each.

   Reply with a number to override, or "ok"/"use recommended" to accept 10.
[Answer]:
```

**No other clarifying questions are needed.** The Epic specifies endpoints, payloads, status codes,
copy, quota values and the proration formula; `requirements.md` resolved the two genuine
uncertainties as assumption A-1 (the $10.00 vs $19.33 discrepancy) and risk R-1 (float vs Decimal
money arithmetic — a design-stage decision, not a story decision). Personas, story format and
acceptance-criteria style are all determinable from the Epic and the existing codebase.

---

## 4. Execution checklist (Part 2 — Generation)

- [ ] Write `personas.md` — the personas implied by the Epic
- [ ] Write `stories.md` beginning with the Parent Epic header line
- [ ] Generate ALL stories in one pass (`story_creation_mode: all-at-once`)
- [ ] Each story: narrative, ≤5 acceptance criteria, persona, requirement trace, files touched
- [ ] Populate the `## Story Tracker` table in `aire-state.md` (`Requires` left blank — filled by the Dependency Graph stage)
- [ ] Step 18.5 — Requirements Coverage Matrix: every FR/NFR/SEC ID fully covered by story ACs
- [ ] Step 18.6 — Granularity check: every story within the sizing ceilings
- [ ] Step 19 — log the generated set in `audit.md`
- [ ] Step 20 — announce the set
- [ ] 🛑 Step 21 — **GATE 1**, halt for explicit approval
- [ ] Step 22 — record the approval response
- [ ] Part 3 — LOCAL: no-op announcement, `Tracker ID = LOCAL` for every story
