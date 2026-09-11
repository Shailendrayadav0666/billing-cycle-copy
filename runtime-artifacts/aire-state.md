# AIRE State — Billing-Cycle

## Tracker
- Type: LOCAL
- Workflow Type: epic
- Parent Epic: EPIC-LOCAL-1 (Mid-Cycle Subscription Upgrade — Standard to Premium)
- Epic URL: none (LOCAL — no external tracker)
- Project Key / Repo / Org: Billing-Cycle (local)

## Team Size
- team_size: 2 (fixed default)

## Branching
- Base Branch: main
- Epic Branch: epic/EPIC-LOCAL-1-mid-cycle-subscription-upgrade

## Code Root
- src/ (canonical — src/backend, src/frontend; no override needed)

## Existing-System Context
- **Workspace type**: brownfield
- **Helix MCP**: connected
- **Source**: atlas
- **Components in scope**: Billing-Cycle (backend/main.py, frontend/src/pages/Billing.jsx, frontend/src/context/AuthContext.jsx)
- **Atlas deep dive doc**: spec/plans/atlas-deep-dive.md
- **Recorded**: 2026-09-11T09:01:49Z

## Helix MCP Binding
- **Server**: helix
- **Docs tool(s)**: mcp__helix__get_solution_document_tool, mcp__helix__list_solution_documents_tool — fetch/list solution documents (epic, deep dive)
- **Graph/Search tool(s)**: mcp__helix__codebase_agent_query, mcp__helix__codebase_cypher_query — natural-language / cypher queries over the codebase graph
- **Estate / workspace id**: solution_id 874 (Billing-Cycle-AIRE-V1-Demo), repo https://github.com/Shailendrayadav0666/Billing-Cycle
- **Resolved**: 2026-09-11T09:01:49Z

## Extension Configuration
- Security Baseline: Enabled = Yes (always mandatory)
- Playwright Test Automation: Enabled = Yes (always mandatory)

## Story Tracker

**Single-story cycle** (user-requested consolidation at GATE 1 — the original 5-story split was
collapsed into one story covering the whole Epic end-to-end; no Dependency Graph file is needed since
there is nothing to graph — `Requires: none`).

| Story | Title | Requires | Tracker ID | Status | Start | End | Recorded |
|-------|-------|----------|------------|--------|-------|-----|----------|
| 1.1 | Mid-Cycle Subscription Upgrade (Standard -> Premium) | none | LOCAL | 🟢 Ready for Development | | | 2026-09-11T09:01:49Z |

## Status
- Analysis complete — awaiting downstream stages
