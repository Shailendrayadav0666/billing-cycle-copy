# Story Generation — Clarification Questions

Your answer to `spec/spec-generation/story-generation.md` ("single story only") conflicts with two
hard framework rules, so I need a confirmation before generating:

1. **Parallelism**: `team_size` is fixed at 2, and story granularity must yield >= 2 independently
   workable stories. A single story means nobody else can start work in parallel.
2. **Step 1.5 hard sizing ceilings** (mechanically enforced, not a style preference): a story bundling
   all 8 functional requirements would very likely exceed 5 acceptance criteria, would newly touch
   *two* architectural layers with real independent logic in each (a proration/state-mutation backend
   endpoint AND a 3-step frontend UI flow — neither is a thin pass-through of the other), and would
   bundle multiple distinct scenario classes (happy-path commit, 401, 400/idempotency, dry-run preview,
   loading/success/error) into one unit of work.

**Important**: even if I generate exactly one story now, the Story Granularity & Splitting Check
(Step 18.6) is an **automatic, mandatory gate with no user override** — it runs right before the
story set is announced and WILL split any story that violates the ceilings above, regardless of the
story count you asked for. So a literal single story is not an achievable end state under this
framework; it will be split before you ever see the "final" set.

## Question 1

How would you like to proceed?

A) Accept that a true single story isn't achievable here — restore the recommended **5 stories**
   (backend commit endpoint, backend dry-run preview, CTA/badge display, confirmation panel, commit
   wiring/loading/error) so the set is compliant from the start, with no forced auto-split later

B) Try the smallest count that can still plausibly pass the sizing ceilings — **2 stories**: one
   backend story (commit + dry-run preview together) and one frontend story (CTA, confirmation panel,
   and commit wiring together). Note: each of these is still likely to hit the ">5 ACs" or
   "two scenario classes" ceiling and may still be auto-split by Step 18.6 — but it's a smaller
   starting point than 5 if you want to see that happen rather than start from the analysis above

C) Generate exactly 1 story anyway, understanding it will almost certainly be auto-split by Step 18.6
   immediately afterward and you'll see a multi-story set regardless

D) Other (please describe after [Answer]: tag below)

[Answer]:
