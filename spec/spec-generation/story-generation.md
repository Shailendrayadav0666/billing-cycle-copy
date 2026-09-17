# Story Generation Plan — Self-Serve Premium Upgrade

## Execution Checklist

- [x] Read `spec/plans/epic-brief.md` and `spec/plans/requirements.md`
- [x] Apply SPIDR slicing to the 8 functional requirements (REQ-F-01..08)
- [ ] Confirm target story count with the user (mandatory question below)
- [ ] Generate all stories in one pass (`story_creation_mode: all-at-once`)
- [ ] Write `stories.md` (Epic header + stories + `Covers` lines) and `personas.md`
- [ ] Populate the Story Tracker in `runtime-artifacts/aire-state.md`
- [ ] Run the Requirements Full-Coverage Check (Step 18.5)
- [ ] Run the Story Granularity & Splitting Check (Step 18.6)
- [ ] Present the complete story set for GATE 1 approval

## Breakdown Approach: Feature-Based, sliced by SPIDR (Interfaces + Paths + Steps)

Single persona (the Standard-plan subscriber), single feature — so **Persona-Based** and
**Domain-Based** breakdowns collapse to the same thing here. **Feature-Based**, then sliced narrower
by SPIDR, is the right fit:

- **Interfaces**: the new backend endpoint (`POST /api/billing/upgrade`) is a separate interface from
  the existing UI (`Billing.jsx`) — split into backend stories and frontend stories.
- **Paths**: within the backend endpoint, the `dry_run` (non-mutating, preview) path and the commit
  (mutating) path are different scenario classes — split into two stories rather than one endpoint
  story with 2 scenario classes bundled.
- **Steps**: the UI is a 3-step workflow (show the CTA -> show the confirmation panel with a live
  preview -> commit with loading/success/error) — split one story per step, per the Step 1.5 rule for
  multi-step workflows.

### Candidate Story Boundaries

| # | Story | SPIDR axis | Covers (REQ-IDs) |
|---|---|---|---|
| 1 | Commit endpoint: proration, plan/usage update, idempotency | Interfaces | REQ-F-05, REQ-F-06, REQ-NF-01, REQ-NF-02, REQ-NF-03, REQ-NF-04, REQ-NF-05 |
| 2 | Dry-run preview endpoint | Interfaces + Paths | REQ-F-07 |
| 3 | Upgrade CTA / Premium badge display | Steps | REQ-F-01, REQ-F-04 |
| 4 | Confirmation panel with live preview | Steps | REQ-F-02 |
| 5 | Commit wiring: loading/success/error + no-regression check | Steps | REQ-F-03, REQ-F-08 |

Each story stays within the Step 1.5 hard sizing ceilings: <=5 ACs, exactly one newly-touched
architectural layer (stories 1-2 backend only, stories 3-5 frontend only), no title conjunction, one
scenario class per story.

## Mandatory Question — Number of Stories

How many user stories should I create for this work?

   Recommended: 5 stories (suggested range: 4-6)

   Why 5:
   - 8 functional requirements SPIDR-sliced along Interfaces (backend endpoint vs UI), Paths (dry_run
     preview vs commit — different scenario classes on the same route), and Steps (the UI's 3-step
     upgrade workflow) into 5 single-purpose stories
   - Keeps >= 2 (team_size) stories runnable in parallel from the start: Story 1 (backend commit
     endpoint) and Story 3 (frontend CTA/badge display) share no code and have no dependency on each
     other, so both can start immediately
   - Each story stays within the Step 1.5 sizing ceilings (<=5 ACs, one architectural layer, one
     scenario class) so review stays small and mechanical

   Reply with a number to override, or "ok"/"use recommended" to accept 5.
[Answer]: 1

## Other Context-Appropriate Questions

None needed — the Epic and PRD (both pulled from Atlas) already fix the personas (one: the Standard
plan user), the story format (AIRE's standard INVEST + acceptance-criteria template), and the
breakdown approach (Feature-Based, above). No additional clarification improves story quality here.
