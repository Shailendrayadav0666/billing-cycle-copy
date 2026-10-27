# Story Generation Plan

**Epic**: HELIX-7344 — Premium Upgrade Demo (Frontend Only)
**Inputs**: `spec/plans/epic-brief.md`, `spec/plans/requirements.md` v1 (REQ-F-01 to REQ-F-12, REQ-NF-01 to REQ-NF-09), `spec/plans/atlas-deep-dive.md`
**team_size**: 2 (fixed framework default, not asked)
**story_creation_mode**: all-at-once (fixed framework default, not asked)
**AIRE Framework**: v1.0

This plan is announced, not approved. Once the questions below are answered, every story is generated in one pass. The complete story set is then presented for your approval (GATE 1). Tracker is Local, so nothing is pushed to an external tracker.

---

## 1. Slicing Analysis (SPIDR)

The Atlas Epic lists one XS story ("Upgrade to Premium Button (Frontend Only)"). Under the AIRE slicing rules, every story must have 5 or fewer acceptance criteria, touch one layer, have no "and" in its title, and cover one scenario class. A single story would break those limits (it covers 21 requirements). So I split it along these axes:

| Capability (requirements) | SPIDR axis used | Resulting story |
|---|---|---|
| Unit test tooling (REQ-NF-05, REQ-NF-06) | Scaffolding that every other story's unit-test gate needs | 1.1 |
| Plan name follows the current plan (REQ-F-07, REQ-F-12) | **R**ules: a rendering rule separate from the upgrade itself | 1.2 |
| Fail-safe billing fetch (REQ-NF-08) | **P**aths: the failure path of the existing fetch | 1.3 |
| Upgrade button shows only on Standard (REQ-F-01, REQ-F-02, REQ-NF-02) | **R**ules: the visibility rule | 1.4 |
| Switch to the Premium values on click (REQ-F-03 to REQ-F-06, REQ-F-08, REQ-NF-01, REQ-NF-04, REQ-NF-07) | **D**ata: the Premium data variant | 1.5 |
| What happens after the upgrade: banner, hidden button, reload reverts (REQ-F-09 to REQ-F-11, REQ-NF-02) | **P**aths: the post-upgrade state | 1.6 |

REQ-NF-03 (styling) is shared out: each story that adds a visual element owns its styles (badge in 1.2, button in 1.4, banner in 1.6).

### Proposed story outline (finalized after your answers)

| Story | Working title | Covers | Likely prerequisites |
|---|---|---|---|
| 1.1 | Frontend unit-test tooling | REQ-NF-05, REQ-NF-06 | none |
| 1.2 | Plan badge and heading follow the current plan | REQ-F-07, REQ-F-12, REQ-NF-03 | 1.1 |
| 1.3 | Fail-safe billing fetch | REQ-NF-08 | 1.1 |
| 1.4 | Upgrade button on the Standard plan | REQ-F-01, REQ-F-02, REQ-NF-02, REQ-NF-03 | 1.1 |
| 1.5 | Switch the plan display to Premium on click | REQ-F-03, REQ-F-04, REQ-F-05, REQ-F-06, REQ-F-08, REQ-NF-01, REQ-NF-04, REQ-NF-07 | 1.2, 1.4 |
| 1.6 | Upgrade confirmation | REQ-F-09, REQ-F-10, REQ-F-11, REQ-NF-02, REQ-NF-03 | 1.5 |

Once 1.1 is merged, 1.2, 1.3 and 1.4 can be built in parallel, which satisfies team_size 2. The Dependency Graph stage confirms the exact `requires` edges.

Note on 1.2: its title has an "and" in it, but badge and heading are one rule ("plan text follows the current plan"), not two behaviours. I'll reword the title at generation so it passes the no-conjunction ceiling.

---

## 2. Breakdown Approaches Considered

| Approach | How it would organise this epic | Trade-off |
|---|---|---|
| **Feature-based with SPIDR slicing** (recommended) | One story per rule, path or data variant (the outline above) | Smallest, most reviewable diffs; ≥ 2 stories run in parallel; more stories than the Epic's single XS item |
| User-journey-based | One story per journey step: see button, click, see Premium, see confirmation | Reads naturally, but the test tooling and the fail-safe fetch have no journey step and would end up bolted onto other stories |
| Persona-based | Stories grouped by subscriber versus demo stakeholder | Little value here: every behaviour is seen by the same subscriber on one page |
| Domain-based | Stories grouped by billing domain concept | The whole epic is one domain concept (plan display), so it collapses into one oversized story |
| Epic-based (hierarchical) | One parent story with sub-stories | Adds a layer with no benefit on a single-page change; the Epic is already the parent |

---

## 3. Execution Checklist

### Part 1: Planning
- [x] Record team_size: 2 (not asked)
- [x] Apply SPIDR slicing to every capability (Section 1)
- [x] Write this plan with embedded questions
- [x] Collect answers to every `[Answer]:` tag
- [x] Analyse answers for ambiguity; ask follow-ups if needed
- [x] Announce the finalized plan (no approval gate)

### Part 2: Generation (all at once)
- [x] Record story_creation_mode: all-at-once
- [x] Generate `spec/plans/personas.md` with the agreed personas
- [x] Generate `spec/plans/stories.md`, first line `EPIC TICKET: HELIX-7344 ...`, with every story:
  - [x] A user-story narrative (As a ... I want ... so that ...)
  - [x] Acceptance criteria in the agreed format, at most 5 per story
  - [x] A `**Covers**:` line naming its REQ-IDs
  - [x] A persona mapping
- [x] Map personas to stories
- [x] Populate `## Story Tracker` in `runtime-artifacts/aire-state.md` (Requires = TBD, Tracker ID = LOCAL, Status = Ready for Development)
- [x] Requirements full-coverage check: all 21 REQ-IDs fully covered; append the Requirements Coverage Matrix to `stories.md`
- [x] Granularity check against the sizing ceilings (5 or fewer ACs, one layer, no title conjunction, one scenario class); split any story that breaks one
- [x] Present the story set for GATE 1 approval

---

## 4. Questions

Please fill in every `[Answer]:` tag below.

## Question 1
 How many user stories should I create for this work?

    Recommended: 6 stories  (suggested range: 5–7)

   Why 6:
   - 21 requirements, sliced by SPIDR into 6 single-purpose stories (2 rules, 2 paths, 1 data variant, plus the test tooling the others need)
   - once 1.1 is merged, 3 stories (1.2, 1.3, 1.4) can run in parallel, so neither of the 2 developers is idle
   - each story stays within the sizing ceilings (5 or fewer ACs, one layer, one scenario class), so each review is small and mechanical
   - 5 is possible if the test tooling is folded into the first feature story (see Question 4); 7 if "reload reverts to Standard" (REQ-F-11) becomes its own story instead of an AC in 1.6

   Reply with a number to override, or "ok"/"use recommended" to accept 6.
[Answer]: ok

## Question 2
Which personas should the stories be written for?

A) Two personas: the **Standard-plan subscriber** (the end user who sees and clicks the button) and the **Product stakeholder** (the demo audience who judges whether the upgrade experience feels right)

B) One persona: the **Standard-plan subscriber** only

X) Other (please describe after [Answer]: tag below)

[Answer]: a

## Question 3
Which breakdown approach should be used? (Trade-offs in Section 2.)

A) Feature-based with SPIDR slicing: one story per rule, path or data variant (the outline in Section 1)

B) User-journey-based: one story per step of the upgrade journey

X) Other (please describe after [Answer]: tag below)

[Answer]: a

## Question 4
Where should the unit-test tooling setup (Vitest, React Testing Library, jsdom) live?

A) In its own first story (1.1) that the other stories require. It keeps tooling separate from feature code and gives a clean, reviewable diff.

B) Inside the first feature story (1.2). One fewer story, but that story then mixes tooling setup with a feature change.

X) Other (please describe after [Answer]: tag below)

[Answer]: a

## Question 5
What format should the acceptance criteria use?

A) Given / When / Then. Each AC becomes one `@AC-n` Gherkin scenario in the story's `.feature` contract at the design checkpoint.

B) A plain checklist of testable statements

X) Other (please describe after [Answer]: tag below)

[Answer]: a
