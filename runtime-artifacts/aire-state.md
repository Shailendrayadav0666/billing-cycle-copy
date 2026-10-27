# aire State Tracking

## Project Information
- **Project Type**: Brownfield
- **Start Date**: 2026-10-27T13:49:14Z
- **Current Stage**: PLANNING - Workflow Planning
- **team_size**: 2 (fixed default, not asked)
- **story_creation_mode**: all-at-once (fixed default, not asked)
- **target_story_count**: 6 (recommended, accepted)
- **Workflow Type**: epic
- **AIRE Framework Version**: 1.0

## Tracker
- Type: LOCAL
- Parent Epic: HELIX-7344 (Atlas Epic document 7344 — "Epic: Premium Upgrade Demo (Frontend Only)")
- Epic URL: —
- Project Key / Repo / Org: —
- Epic Content Source: Helix MCP (user-directed) — spec/plans/epic-brief.md

## Workspace State
- **Existing Code**: Yes
- **Programming Languages**: Python (backend), JavaScript/JSX (frontend)
- **Build System**: pip (src/backend/requirements.txt), npm (src/frontend/package.json)
- **Project Structure**: Monolith — FastAPI API + React SPA in one repo
- **Workspace Root**: C:\Users\shailendra.yadav\Desktop\projects\helix-aire-v1-demo1\billing-cycle-copy
- **Reverse Engineering Needed**: No — Atlas deep dive pulled (Reverse Engineering SKIPPED)
- **Reverse Engineering Artifacts**: spec/plans/atlas-deep-dive.md

## Code Location Rules
- **Application Code**: src/ (existing code already under src/ — no Code Root override)
- **Documentation**: spec/ only
- **Structure patterns**: See code-generation.md Critical Rules

## Helix MCP Binding
- **Server**: helix
- **Docs tool(s)**: list_solution_documents_tool, get_solution_document_tool — list and fetch Atlas solution documents (Epic, deep dive)
- **Graph/Search tool(s)**: codebase_agent_query, codebase_cypher_query, document_chatbot_query, graph_change_impact — targeted relationship/doc questions for inline answers
- **Docs write tool(s)**: save_solution_document_tool — create (parent_registry_id + visibility_intent user_team) / replace by document_id
- **Estate / workspace id**: Billing-Cycle-Helix-Workshop (solution_id 951), repository Billing-Cycle @ main, last_ingested_commit 69f67f308492a85648aa25a9ff7d8d574031344a
- **Resolved**: 2026-10-27T13:50:18Z

## Atlas Artifact Sync
- Enabled: Yes
- Source: user opt-in
- Cycle Folder: HELIX-7344-premium-upgrade-demo-frontend-only (doc 7816)
- Decided At: 2026-10-27T13:54:32Z

### Synced Files
| Path | Doc ID | Synced At |
|------|--------|-----------|
| ./ | 7816 | 2026-10-27T13:54:32Z |
| spec/ | 7817 | 2026-10-27T13:54:32Z |
| spec/plans/ | 7820 | 2026-10-27T13:54:32Z |
| spec/spec-generation/ | 7821 | 2026-10-27T13:54:32Z |
| spec/behavior/ | 7822 | 2026-10-27T13:54:32Z |
| spec/test-plans/ | 7823 | 2026-10-27T13:54:32Z |
| spec/playwright-specs/ | 7824 | 2026-10-27T13:54:32Z |
| runtime-artifacts/ | 7818 | 2026-10-27T13:54:32Z |
| runtime-artifacts/stories/ | 7825 | 2026-10-27T13:54:32Z |
| reports/ | 7819 | 2026-10-27T13:54:32Z |
| reports/unit-test-evidence/ | 7826 | 2026-10-27T13:54:32Z |
| reports/behavior-test-evidence/ | 7827 | 2026-10-27T13:54:32Z |
| reports/api-contract-test-evidence/ | 7828 | 2026-10-27T13:54:32Z |
| reports/playwright-test-evidence/ | 7829 | 2026-10-27T13:54:32Z |
| reports/eval-evidence/ | 7830 | 2026-10-27T13:54:32Z |
| reports/reviews/ | 7831 | 2026-10-27T13:54:32Z |
| reports/code-security-reviews/ | 7832 | 2026-10-27T13:54:32Z |
| reports/ticket-summary/ | 7833 | 2026-10-27T13:54:32Z |
| reports/pr-feedback/ | 7834 | 2026-10-27T13:54:32Z |
| spec/plans/epic-brief.md | 7835 | 2026-10-27T14:11:50Z |
| spec/plans/requirements.md | 7837 | 2026-10-27T14:11:50Z |
| spec/spec-generation/requirement-verification-questions.md | 7838 | 2026-10-27T14:11:50Z |
| spec/plans/atlas-deep-dive.md | 7839 | 2026-10-27T14:11:50Z |
| runtime-artifacts/aire-state.md | 7840 | 2026-10-27T14:26:18Z |
| runtime-artifacts/audit.md | 7841 | 2026-10-27T14:26:18Z |
| spec/plans/stories.md | 7842 | 2026-10-27T14:23:50Z |
| spec/plans/personas.md | 7843 | 2026-10-27T14:23:50Z |
| spec/plans/dependency-graph.yml | 7844 | 2026-10-27T14:23:50Z |
| spec/spec-generation/story-generation.md | 7845 | 2026-10-27T14:23:50Z |

### Pending
| Path | Reason |
|------|--------|

## Context Project
- **Existing Knowledge**: No
- **Existing Knowledge Path(s)**: —
- **New References**: No
- **New Reference Path(s)**: —

## Design References
| # | Path / Location | Type | Governs | Read? | Read At Stage |
|---|-----------------|------|---------|-------|---------------|

## Existing-System Context
- **Workspace type**: brownfield
- **Helix MCP**: connected
- **Source**: atlas
- **Components in scope**: frontend Billing page (src/frontend/src/pages/Billing.jsx), frontend styles (src/frontend/src/App.css), read-only backend GET /api/billing contract (src/backend/main.py)
- **Atlas deep dive doc**: spec/plans/atlas-deep-dive.md
- **Recorded**: 2026-10-27T13:52:14Z

## Branching
- Base Branch: main
- Epic Branch: epic/HELIX-7344-premium-upgrade-demo-frontend-only
- Epic PR: (not raised — raised manually at cycle end via pr-generator)

## Extension Configuration
| Extension | Enabled | Decided At |
|---|---|---|
| Security Baseline | Yes (always enforced) | Workspace Detection |
| UI/UX Mockups | No | Requirements Analysis |
| Resiliency Baseline | No | Requirements Analysis |
| Property-Based Testing | No | Requirements Analysis |

## UI/UX Design
- **Mode**: skip
- **Provided design path(s)**: —
- **Decided At**: Requirements Analysis

## Story Tracker

| Story | Title | Requires | Tracker ID | Status | PR | Merged | Start | End | Recorded |
|-------|-------|----------|------------|--------|----|--------|-------|-----|----------|
| 1.1 | Frontend unit-test tooling | none | LOCAL | Ready for Development | — | — | | | 2026-10-27T14:19:58Z |
| 1.2 | Plan text follows the current plan | 1.1 | LOCAL | Ready for Development | — | — | | | 2026-10-27T14:19:58Z |
| 1.3 | Fail-safe billing fetch | 1.1 | LOCAL | Ready for Development | — | — | | | 2026-10-27T14:19:58Z |
| 1.4 | Upgrade button on the Standard plan | 1.1 | LOCAL | Ready for Development | — | — | | | 2026-10-27T14:19:58Z |
| 1.5 | Switch the plan display to Premium on click | 1.2, 1.4 | LOCAL | Ready for Development | — | — | | | 2026-10-27T14:19:58Z |
| 1.6 | Post-upgrade confirmation | 1.5 | LOCAL | Ready for Development | — | — | | | 2026-10-27T14:19:58Z |

## Dependency Graph

Generated 2026-10-27T14:19:58Z (auto-generated, no approval gate). Source: `spec/plans/dependency-graph.yml`.

```mermaid
graph TD
    S1_1["1.1 Frontend unit-test tooling"]
    S1_2["1.2 Plan text follows the current plan"]
    S1_3["1.3 Fail-safe billing fetch"]
    S1_4["1.4 Upgrade button on the Standard plan"]
    S1_5["1.5 Switch the plan display to Premium on click"]
    S1_6["1.6 Post-upgrade confirmation"]
    S1_1 --> S1_2
    S1_1 --> S1_3
    S1_1 --> S1_4
    S1_2 --> S1_5
    S1_4 --> S1_5
    S1_5 --> S1_6
```

Text alternative: 1.1 first; then 1.2, 1.3 and 1.4 in parallel; 1.5 after 1.2 and 1.4; 1.6 after 1.5.

**Ready now**: 1.1 (no prerequisites).
**Blocked**: 1.2, 1.3, 1.4 by 1.1 | 1.5 by 1.2 and 1.4 | 1.6 by 1.5.
**Parallelism**: once 1.1 merges, 3 stories (1.2, 1.3, 1.4) are available at once (>= team_size 2). Only one story is startable at the very beginning because 1.1 is the R1 seed for the test tooling.

| Edge | Justification |
|---|---|
| 1.2 requires 1.1 | R1: its unit tests need the Vitest/RTL/jsdom setup 1.1 creates |
| 1.3 requires 1.1 | R1: its unit tests need the Vitest/RTL/jsdom setup 1.1 creates |
| 1.4 requires 1.1 | R1: its unit tests need the Vitest/RTL/jsdom setup 1.1 creates; reads plan_name directly, so no edge to 1.2 (R4) |
| 1.5 requires 1.2 | R2: AC-1 relies at runtime on the plan-text rule from 1.2 |
| 1.5 requires 1.4 | R2: the click handler is wired onto the button 1.4 renders |
| 1.6 requires 1.5 | R2: banner and hidden button react to the post-upgrade state 1.5 introduces |

**Shared files** (rebase before merge when built in parallel): src/frontend/src/pages/Billing.jsx, src/frontend/src/App.css, the Billing page unit test file.

## Stage Progress
- [x] Workspace Detection — state check, tracker selection, Parent Epic capture (Helix), code scan, Helix MCP gate, Epic branch, context folders
- [x] Workspace Detection — Atlas Artifact Sync opt-in (Yes), Context opt-in (1 no, 2 no), design reference guardrail loaded
- [x] Reverse Engineering — SKIPPED (Atlas deep dive found and pulled)
- [x] Requirements Analysis — depth Standard; spec/plans/requirements.md v1 (REQ-F-01..12, REQ-NF-01..09) approved 2026-10-27T14:04:48Z
- [x] User Stories — 6 stories (spec/plans/stories.md, personas.md); GATE 1 approved 2026-10-27T14:19:58Z; Part 3 push skipped by design (Type: LOCAL, Tracker ID LOCAL)
- [x] Dependency Graph — spec/plans/dependency-graph.yml (auto, no gate)
- [ ] Workflow Planning
- [ ] Application Design (conditional)
