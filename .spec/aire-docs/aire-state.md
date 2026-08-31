# aire State Tracking

## Project Information
- **Project Type**: Brownfield
- **Start Date**: 2026-08-31T11:07:03Z
- **Current Stage**: PLANNING - Requirements Analysis
- **AIRE Version**: 1.0
- **Workflow Type**: Epic

## Workspace State
- **Existing Code**: Yes
- **Programming Languages**: Python (FastAPI backend), JavaScript/JSX (React 19 frontend), CSS, HTML
- **Build System**: npm + Vite 8 (frontend); pip / requirements.txt (backend)
- **Project Structure**: Full-stack monolith (POC) — single FastAPI module + React SPA
- **Workspace Root**: C:/Users/shailendra.yadav/Desktop/projects/helix-aire-v1-demo2
- **Reverse Engineering Needed**: No — Atlas full coverage (see Existing-System Context)
- **Reverse Engineering Artifacts**: .spec/aire-docs/planning/reverse-engineering/

## Code Root
- **Backend**: src/backend/ (FastAPI — main.py, requirements.txt)
- **Frontend**: frontend/ (React 19 + Vite SPA — pre-existing location, NOT moved)
- **Note**: This brownfield repo keeps the frontend outside src/. Both roots are treated as the code root for this cycle. No tree is moved.
- **Recorded**: 2026-08-31T11:07:03Z

## Code Location Rules
- **Application Code**: src/backend/ and frontend/ (NEVER in .spec/aire-docs/)
- **Documentation**: .spec/ only
- **Tests**: tests/unit/, tests/behavior/, tests/e2e/

## Helix MCP Binding
- **Server**: helix
- **Graph tool(s)**: mcp__helix__codebase_agent_query — natural-language codebase graph queries; mcp__helix__codebase_cypher_query — direct Cypher; mcp__helix__graph_change_impact — change-impact analysis
- **Docs tool(s)**: mcp__helix__list_solution_documents_tool, mcp__helix__get_solution_document_tool — list/fetch Atlas solution documents; mcp__helix__document_chatbot_query — NL query over docs
- **Search tool(s)**: mcp__helix__document_chatbot_query, mcp__helix__platform_docs_query
- **Estate / workspace id**: solution_id 874 — "Billing-Cycle-AIRE-V1-Demo"; repository Billing-Cycle (https://github.com/Shailendrayadav0666/Billing-Cycle), branch main, last ingested commit bcec649e08f2dbec435c24066deae6a1d6d71192
- **Resolved**: 2026-08-31T11:07:03Z

## Existing-System Context
- **Workspace type**: brownfield
- **Helix MCP**: connected
- **Source**: atlas
- **Components in scope**: backend (FastAPI main.py), frontend Billing page (Billing.jsx), frontend AuthContext.jsx, frontend App.jsx
- **Atlas coverage**: 8 of 8 components covered by the "Deep Dive: Billing-Cycle" document (id 3155, v28, CURRENT)
- **Knowledge graph**: .spec/aire-docs/planning/reverse-engineering/knowledge-graph.md
- **Recorded**: 2026-08-31T11:07:03Z

## Tracker
- Type: LOCAL
- Parent Epic: EPIC-1 (locally minted — Epic sourced from Atlas document 3157, not from an external tracker)
- Epic URL: -
- Project Key / Repo / Org: -
- Note: LOCAL mode. Zero external tracker calls, ever. The Story Tracker in this file is authoritative.

## Branching
- Base Branch: main
- Epic Branch: epic/EPIC-1-mid-cycle-subscription-upgrade
- Epic PR: (not raised - raised manually at cycle end via pr-generator)

## Context Project
- **Existing Knowledge**: No
- **Existing Knowledge Path(s)**: -
- **New References**: No
- **New Reference Path(s)**: -
- **Note**: User answered "no" to both parts. Existing-system knowledge comes from Atlas instead.

## Design References
| Reference | Type | Registered At Stage | Read? | Read At Stage |
|---|---|---|---|---|
| Atlas document 3157 (Epic: Mid-Cycle Subscription Upgrade) | Solution document (epic) | Workspace Detection | Yes | Workspace Detection |
| Atlas document 3155 (Deep Dive: Billing-Cycle) | Solution document (deepdive) | Workspace Detection | Yes | Workspace Detection |

### Reconciliations
| Point | Reference says | Decision taken | Why |
|---|---|---|---|
| Repo layout | `backend/` + `frontend/` at repo root | Mapped to `src/backend/` + `frontend/` | Atlas describes the upstream Billing-Cycle repo; this workspace is an AIRE-restructured copy. Atlas remains the truth for architecture and contracts; only paths are remapped. |
| `renew_at` value | Hardcoded string "Sep 09, 2025" | Treated as dynamic (`today + 30 days`) | Verified in `src/backend/main.py` lines 27, 35, 125, 130 - `renew_at` is computed at runtime. The Epic's "$10.00 at 15 days" is an illustrative example, not a fixture. |

## Story Tracker
| Story | Title | Requires | Tracker ID | Status | PR | Merged | Start | End | Recorded |
|---|---|---|---|---|---|---|---|---|---|
| (to be populated by the User Stories stage) | | | | | | | | | |

## Team Configuration
- team_size: 2 (fixed default - never asked)
- story_creation_mode: all-at-once (fixed default - never asked)

## Extension Configuration
| Extension | Enabled | Source |
|---|---|---|
| Security Baseline | Yes (ALWAYS mandatory) | extensions/security/baseline/security-baseline.md |
| Playwright Test Automation | Yes (ALWAYS mandatory) | extensions/testing/playwright-automation/playwright-automation.md |
| Resiliency Baseline | No (user declined) | extensions/resiliency/baseline/resiliency-baseline.opt-in.md |
| Property-Based Testing | No (user declined) | extensions/testing/property-based/property-based-testing.opt-in.md |

## Stage Progress
- [x] Workspace Detection — COMPLETE
- [x] Reverse Engineering — SKIPPED (Atlas full coverage, Source: atlas)
- [ ] Requirements Analysis — in progress
- [ ] User Stories
- [ ] Dependency Graph
- [ ] Workflow Planning
- [ ] Application Design
