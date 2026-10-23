# Story Generation Plan: Premium Upgrade Demo (Frontend Only)

**Epic**: Atlas document 7344 (LOCAL tracker)
**Inputs**: `spec/plans/requirements.md` v1 (REQ-F-01 to REQ-F-10, REQ-NF-01 to REQ-NF-06), `spec/plans/epic-brief.md`, `spec/plans/atlas-deep-dive.md`, Atlas story doc 7342
**team_size**: 2 (fixed framework default)
**story_creation_mode**: all-at-once (fixed framework default)

---

## 1. Slicing Analysis (SPIDR)

| Capability | SPIDR axis | Candidate story | REQ-IDs |
|---|---|---|---|
| Unit-test runner and regression safety net for the existing Billing page | Enabler with standalone value (a characterization test of today's display backs REQ-NF-02) | Regression test baseline for the Billing page | REQ-NF-02, REQ-NF-04, REQ-NF-05 |
| Plan badge and section heading driven by `plan_name` | **D: Data** (labels move from hardcoded text to data) | Plan labels reflect the current plan | REQ-F-05, REQ-F-09 |
| Button shown only for Standard | **R: Rules** (visibility rule on `plan_name`) | Upgrade button visible only on the Standard plan | REQ-F-01, REQ-F-02, REQ-F-08, REQ-NF-03 (button) |
| Click switches the page to Premium | **P: Paths** (the happy-path upgrade interaction) | Upgrade switches the Billing page to Premium | REQ-F-03, REQ-F-04, REQ-F-06, REQ-F-07, REQ-F-10, REQ-NF-01, REQ-NF-03 (status), REQ-NF-06 |

**Parallelism with team_size 2:** once the baseline story lands, the labels story and the button story are independent of each other and can run in parallel. The upgrade-click story owns the seam between them: after the click, the labels read Premium and the button disappears.

**Sizing ceilings:** every candidate has at most 5 ACs, touches one layer (the frontend Billing page), has no "and"/"or" in its title, and covers one scenario class.

## 2. Breakdown Approach

- **Feature-based, sliced by SPIDR** (chosen). Stories map to the distinct rules, data and path facets of the one feature, which keeps each diff small and reviewable.
- User-journey-based (not chosen). A single journey ("Standard user upgrades") would produce one story of more than 5 ACs spanning several scenario classes, which breaks the sizing ceilings.
- Persona-, domain- and epic-based approaches (not chosen). There is one persona journey and one domain, so they add nothing here.

## 3. Execution Checklist

- [x] Write `spec/plans/stories.md`, starting with the `EPIC TICKET:` header line
- [x] Generate all stories in one pass, each with a narrative, Given/When/Then ACs, persona and a `**Covers**:` line
- [x] Write `spec/plans/personas.md` (Standard plan subscriber, Demo presenter, Frontend developer) and map personas to stories
- [x] Check every story against INVEST and the Step 1.5 sizing ceilings
- [x] Populate the `## Story Tracker` in `runtime-artifacts/aire-state.md` (Requires = TBD, Tracker ID = LOCAL)
- [x] Run the Requirements Coverage Matrix and full-coverage check (Step 18.5)
- [x] Run the granularity and splitting check (Step 18.6)
- [x] Present GATE 1 (story set approval)

## 4. Questions

### Question 1

```
 How many user stories should I create for this work?

    Recommended: 4 stories  (suggested range: 3–4)

   Why 4:
   - 16 REQ-IDs SPIDR-sliced into one Rules story (button visibility), one Data story (data-driven
     plan labels) and one Paths story (the upgrade click), plus a regression-baseline story that
     installs the missing test runner and locks in today's Billing display (REQ-NF-02/04/05)
   - after the baseline lands, the labels and button stories run in parallel, so team_size 2 has
     no idle developer; with 3 stories (baseline folded into the labels story) the chain is fully
     sequential
   - each story stays within the Step 1.5 sizing ceilings (5 ACs or fewer, one layer, one scenario
     class), so each review is small and mechanical

   Reply with a number to override, or "ok"/"use recommended" to accept 4.
[Answer]: 1
```


> **Decision**: Story count 1 (Q1 = 1, confirmed `story-clarification-questions.md` Q1 = A — single story, sizing-ceiling override). The candidate slices in Section 1 are retained as ACs of Story 1.1.
