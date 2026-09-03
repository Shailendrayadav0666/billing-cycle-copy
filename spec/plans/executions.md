# Execution Plan

## Detailed Analysis Summary

### Transformation Scope (Brownfield)
- **Transformation Type**: Single component change — additive feature within the existing `backend/main.py` and `frontend/src/pages/Billing.jsx`, no new services/packages/deployment units.
- **Primary Changes**: 2 new FastAPI endpoints (`GET /api/billing/upgrade-preview`, `POST /api/billing/upgrade`), 1 new pure function (`charge_card`), 3 new backend constants; 1 modified frontend page (dynamic badge, CTA, confirmation modal, success/error handling).
- **Related Components**: None beyond the two files above — `AuthContext.jsx` (read-only reference for the email-as-token pattern), `App.jsx` route (unchanged).

### Change Impact Assessment
- **User-facing changes**: Yes — new CTA, modal, success banner, and inline error state on the Billing page.
- **Structural changes**: No — no new architectural layers, no new services, no routing changes.
- **Data model changes**: No new entities — extends the existing `billing_data`/`users` in-memory dict shapes with values already fully specified in `requirements.md`/`stories.md` (no schema design needed).
- **API changes**: Yes — 2 new endpoints, fully specified (request/response shapes, status codes) in the approved requirements and story.
- **NFR impact**: Minor and already fully captured as REQ-NF-01..05 (server-side-only math, zero new dependencies, deterministic gateway, consistent error conventions, accepted in-memory-store limitation) — no open NFR question remains.

### Component Relationships (Brownfield)
- **Primary Component**: Billing feature (`backend/main.py` billing section + `frontend/src/pages/Billing.jsx`)
- **Infrastructure Components**: None (no DB, no new deployment target)
- **Shared Components**: None modified (`AuthContext.jsx` read-only)
- **Dependent Components**: None — no other page/module consumes the billing endpoints
- **Supporting Components**: None (no new monitoring/logging needed for a POC)

### Risk Assessment
- **Risk Level**: Low — isolated to one existing page and one existing backend module; no auth, infra, or cross-service impact; easy rollback (revert the single commit/PR).
- **Rollback Complexity**: Easy
- **Testing Complexity**: Simple — deterministic gateway makes both outcomes (success/decline) trivially reproducible for unit and manual testing.

## Workflow Visualization

```mermaid
flowchart TD
    Start(["User Request"])

    subgraph PLANNING["Blue: PLANNING PHASE"]
        WD["Workspace Detection<br/><b>COMPLETED</b>"]
        RE["Reverse Engineering<br/><b>SKIPPED (Full Atlas coverage)</b>"]
        RA["Requirements Analysis<br/><b>COMPLETED</b>"]
        US["User Stories<br/><b>COMPLETED</b>"]
        DG["Dependency Graph<br/><b>COMPLETED</b>"]
        WP["Workflow Planning<br/><b>IN PROGRESS</b>"]
        AD["Application Design<br/><b>SKIP</b>"]
    end

    subgraph IMPLEMENTATION["Green: IMPLEMENTATION PHASE"]
        FD["Functional Design<br/><b>SKIP</b>"]
        NFRA["NFR Requirements<br/><b>SKIP</b>"]
        NFRD["NFR Design<br/><b>SKIP</b>"]
        ID["Infrastructure Design<br/><b>SKIP</b>"]
        STOP[" STOP CHECKPOINT<br/><b>MANDATORY HALT</b>"]
        CG["Code Generation (dev-implement)<br/><b>EXECUTE</b>"]
    end

    subgraph veTRACK["Teal: ve TRACK - parallel, ve-initiated"]
        BT["Test Plan per story<br/><b>/ve-implement</b>"]
        QS["ve Sign-off<br/><b>ve-list-work</b>"]
    end

    Start --> WD
    WD -.-> RE
    WD --> RA
    RE --> RA
    RA --> US
    US --> DG
    DG --> WP
    WP -.-> AD
    WP --> STOP
    STOP -->|dev-implement| CG
    US -.->|ve in parallel| BT
    BT --> QS
    CG --> QS
    QS --> End(["Complete"])

    style WD fill:#4CAF50,stroke:#1B5E20,stroke-width:3px,color:#fff
    style RA fill:#4CAF50,stroke:#1B5E20,stroke-width:3px,color:#fff
    style US fill:#4CAF50,stroke:#1B5E20,stroke-width:3px,color:#fff
    style DG fill:#4CAF50,stroke:#1B5E20,stroke-width:3px,color:#fff
    style WP fill:#4CAF50,stroke:#1B5E20,stroke-width:3px,color:#fff
    style STOP fill:#E53935,stroke:#B71C1C,stroke-width:3px,color:#fff
    style CG fill:#4CAF50,stroke:#1B5E20,stroke-width:3px,color:#fff
    style RE fill:#BDBDBD,stroke:#424242,stroke-width:2px,stroke-dasharray: 5 5,color:#000
    style AD fill:#BDBDBD,stroke:#424242,stroke-width:2px,stroke-dasharray: 5 5,color:#000
    style FD fill:#BDBDBD,stroke:#424242,stroke-width:2px,stroke-dasharray: 5 5,color:#000
    style NFRA fill:#BDBDBD,stroke:#424242,stroke-width:2px,stroke-dasharray: 5 5,color:#000
    style NFRD fill:#BDBDBD,stroke:#424242,stroke-width:2px,stroke-dasharray: 5 5,color:#000
    style ID fill:#BDBDBD,stroke:#424242,stroke-width:2px,stroke-dasharray: 5 5,color:#000
    style BT fill:#26A69A,stroke:#00695C,stroke-width:3px,color:#fff
    style QS fill:#26A69A,stroke:#00695C,stroke-width:3px,color:#fff
    style Start fill:#CE93D8,stroke:#6A1B9A,stroke-width:3px,color:#000
    style End fill:#CE93D8,stroke:#6A1B9A,stroke-width:3px,color:#000

    linkStyle default stroke:#333,stroke-width:2px
```

## Phases to Execute

### PLANNING PHASE
- [x] Workspace Detection (COMPLETED)
- [x] Reverse Engineering (SKIPPED — Full Atlas coverage via Helix MCP)
- [x] Requirements Analysis (COMPLETED)
- [x] User Stories (COMPLETED — 1 story, user-overridden granularity)
- [x] Dependency Graph (COMPLETED — no dependencies, single story)
- [x] Workflow Planning (IN PROGRESS)
- [ ] Application Design - **SKIP**
  - **Rationale**: No new components or services; the work stays entirely within the existing `backend/main.py` and `Billing.jsx` component boundaries. Endpoint/function signatures are already fully specified in `stories.md`.

### IMPLEMENTATION PHASE
- [ ] Functional Design - **SKIP**
  - **Rationale**: The one piece of non-trivial business logic (proration formula) is already fully specified with exact formulas and a worked example in `requirements.md`/`stories.md` — no remaining design ambiguity.
- [ ] NFR Requirements - **SKIP**
  - **Rationale**: Tech stack is already fixed (existing FastAPI/React POC); all NFRs identified (REQ-NF-01..05) are already fully captured in `requirements.md` with no open question.
- [ ] NFR Design - **SKIP**
  - **Rationale**: NFR Requirements skipped — nothing to incorporate.
- [ ] Infrastructure Design - **SKIP**
  - **Rationale**: No infrastructure changes — in-memory store, no new deployment target, no new cloud resources.
- [ ] Code Generation - **EXECUTE (ALWAYS)**
  - **Rationale**: Implementation is required to deliver the epic; triggered per-story via `dev-implement` after the mandatory STOP CHECKPOINT.

### ve TRACK (parallel — ve-initiated, NOT planned or executed by this workflow)
- Test Plan — run per story by ve with `/ve-implement`, in parallel with development
- ve Sign-off — run by ve with `ve-list-work` on the epic branch once the story PR merges
  - **Rationale**: Test Plan is not an Implementation stage at epic or story level; it is not scheduled here and is never auto-run

## Package Change Sequence
Not applicable — single-repo, single-module POC (no multi-package coordination).

## Estimated Timeline
- **Total Phases Executing**: Workspace Detection, Requirements Analysis, User Stories, Dependency Graph, Workflow Planning, STOP Checkpoint (architecture.md + rubrics + CI), Code Generation (1 story)
- **Estimated Duration**: ~3.5 days of estimated effort per the Epic's own estimate (Story 1 consolidates the Epic's original 5-story, ~3.5-day estimate into one story)

## Success Criteria
- **Primary Goal**: Standard subscribers can self-serve upgrade to Premium mid-cycle with correct proration and a deterministic dummy payment outcome.
- **Key Deliverables**: 2 new backend endpoints, `charge_card()`, updated `Billing.jsx` (dynamic plan display, CTA, modal, success/error handling), unit tests, `architecture.md`, CI pipeline.
- **Quality Gates**: Unit + coverage, Gherkin behaviour spec (B1-B3), API & Contract Testing Gate (new endpoints), full regression vs baseline, static D1-D7, automated code review incl. Security Baseline diff-scoped review, blocking J1/J2 judge gates.
- **Integration Testing**: Manual verification of both `charge_card` outcomes (success / `fail*` email) end-to-end through the UI.
- **Operational Readiness**: N/A for this POC — no monitoring/alerting infrastructure exists or is being added.
