# Functional Design Plan — EPIC-1

**Depth**: Standard · **Scope**: system-level, scoped to `epic-brief.md`
**Stage status**: artifacts written; awaiting approval

## Inputs loaded
- [x] `planning/requirements/epic-brief.md` — Atlas doc 3157 (WHAT to build)
- [x] `planning/requirements/requirements.md` — FR/NFR/SEC set
- [x] `planning/user-stories/stories.md` + `## Story Tracker` — Story 1.1, 31 ACs
- [x] `planning/reverse-engineering/knowledge-graph.md` — Atlas doc 3155 (existing = starting state)
- [x] Application Design artifacts — N/A, stage skipped by the execution plan
- [x] `## Context Project` — no artifacts, no references (user declined)

## Execution checklist
- [x] Resolve **D-1**: money arithmetic — float + round vs Decimal (risk R-1)
- [x] Resolve **D-2**: mutation strategy for provable NFR-5 atomicity
- [x] Resolve **D-3**: Premium quota merge preserving `used` (AC-21)
- [x] Model the domain-entity delta (no invented entities)
- [x] Enumerate business rules BR-1..BR-10, each traced to an AC
- [x] Define the two endpoints, two internal helpers, and the gateway function
- [x] Define the frontend component delta, state shape and transitions
- [x] Record what is deliberately left unchanged, with reasons
- [x] Content validation before file creation (Mermaid quoted labels; no section-sign character)
- [x] Present the standardized 2-option completion message
- [ ] Await explicit approval
- [ ] Log approval and mark the stage complete

## Artifacts produced
| File | Contents |
|---|---|
| `design/functional-design/domain-entities.md` | Existing entities + delta, new constants, request/response shapes, ER diagram |
| `design/functional-design/business-rules.md` | BR-1..BR-10 with AC traces, invariants, evaluation-order diagram |
| `design/functional-design/business-logic-model.md` | Decisions D-1..D-3, function and endpoint designs, happy/declined sequences, deliberate non-changes |
| `design/functional-design/frontend-components.md` | Component tree delta, state shape and transitions, render changes, data flow, error handling, CSS, accessibility |
