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

## Environment Notes
- **Podman**: machine running (`podman ps` connects), but outbound pulls from docker.io **structurally blocked** from inside the WSL VM (verified with 2 images/IPs, `dial tcp ...:443: i/o timeout` both times — proxy/firewall not covering the VM's network namespace). User-approved deviation (2026-09-11): proceed WITHOUT container-based validation for this cycle. Effects: actionlint validation skipped (YAML produced by pure slot-substitution into the pre-vetted framework template, not freehand-authored); the Behavioural Gherkin gate (B1/B2/B3) will run natively (pytest-bdd, no Podman) with `"containerised": false, "reason": "podman machine has no outbound network access to docker.io (verified, not transient)"` recorded on every tier; SonarQube Option B (self-hosted Community Build) is unavailable — Option A (SonarQube Cloud) only, if SonarQube is used at all.

## SonarQube Setup Gate
- **Answer**: proceed (2026-09-11T09:01:49Z)
- User confirmed CLAUDE_CODE_OAUTH_TOKEN, SONAR_TOKEN, SONAR_HOST_URL added as GitHub Actions repository secrets, and set `sonar-project.properties` `sonar.projectKey=shailendrayadav0666_billing-cycle-copy`, `sonar.projectName=billing-cycle-copy`, `sonar.organization=shailendrayadav0666` (Option A — SonarQube Cloud; Option B self-hosted was unavailable, see Environment Notes). Secret values were not and cannot be verified from here — the first pipeline run is what proves them. `tests/.evals/config.json` `sonarqube.enabled = true`; `sonarqube` appended to `ci.gates`.

## Status
- Design complete — awaiting dev-implement
