# Execution Plan — EPIC-1 Mid-Cycle Subscription Upgrade

**Epic**: EPIC-1 (LOCAL) · Atlas doc 3157
**Branch**: `epic/EPIC-1-mid-cycle-subscription-upgrade` (base `main`)
**AIRE Version**: 1.0
**Created**: 2026-08-31
**Status**: 🤖 auto-approved — announcement only, no gate

---

## 1. Inputs consulted

| Input | Summary |
|---|---|
| **User request** | "using aire and helix mcp fetch the solution document and start implementing the epic requirements" |
| **Existing system** (brownfield) | Full-stack POC monolith. FastAPI single module (`src/backend/main.py`, 212 LOC) with three in-memory dicts as the data layer; React 19 + Vite 8 SPA (`src/frontend/`). 6 existing endpoints. **Zero tests. No CI for the app.** Atlas doc 3155. |
| **Requirements** | FR-1..FR-13, NFR-1..NFR-7, SEC-1..SEC-6. 6 Epic assumptions confirmed, 6 corrected (F-1..F-6). |
| **User stories** | 1 story (user override of the recommended 10), 31 ACs, 26/26 requirement coverage. |
| **Dependency graph** | Single node, no edges, immediately startable. |
| **Context project** | Not used (user declined both parts). |

## 2. Risk and impact analysis

| Dimension | Assessment |
|---|---|
| **Risk level** | **Medium** |
| **Why medium, not low** | Money-adjacent arithmetic; a mutation spanning two data structures with no transaction; zero existing tests means no regression net; the single-story shape means one 3-attempt self-healing budget covers all 13 functional requirements. |
| **Why not high** | No auth change, no schema migration, no infrastructure change, no new dependency, no external integration. The blast radius is two files. |
| **Components affected** | `src/backend/main.py` (new: `UpgradeRequest`, `PLANS`, `PREMIUM_QUOTAS`, `DAYS_IN_CYCLE`, `charge_card()`, two endpoints) · `src/frontend/src/pages/Billing.jsx` (dynamic plan render, CTA, modal, success/failure handling) |
| **Components read but NOT changed** | `src/frontend/src/context/AuthContext.jsx` (supplies `token`) · `src/frontend/src/App.jsx` (routing) · `src/frontend/vite.config.js` (existing `/api` proxy already covers the new routes) |
| **Key impacts** | `GET /api/billing`'s response is consumed differently by the UI (`plan_name` now rendered). `users` and `billing_data` become mutable post-registration for the first time. |

---

## 3. Recommended execution plan — 6 stages to execute

### 🔵 PLANNING PHASE

| # | Stage | Status | Rationale |
|---|---|---|---|
| 1 | Workspace Detection | ✅ done | Always executes. Classified brownfield, resolved the split code root, bound Helix. |
| 2 | Reverse Engineering | ⏭️ skipped | Atlas coverage FULL — see the skip list below. |
| 3 | Requirements Analysis | ✅ done | Always executes. Standard depth; corrected 6 Epic assumptions against live code. |
| 4 | User Stories | ✅ done | Always executes. GATE 1 approved. |
| 5 | Dependency Graph | ✅ done | Always executes. |
| 6 | **Workflow Planning** | ▶️ this stage | Always executes. |
| 7 | Application Design | ⏭️ skip | See skip list. |

### 🟢 IMPLEMENTATION PHASE

| # | Stage | Depth | Rationale |
|---|---|---|---|
| 8 | **Functional Design** | Standard | **Genuinely needed.** Three real decisions remain open that the Epic does not settle: (a) **risk R-1** — `20.0 / 30` is float money arithmetic; whether to use `Decimal` or keep the Epic's float + `round()` is a design decision with correctness consequences; (b) **NFR-5 atomicity** — the exact mutation ordering that makes a declined card provably non-mutating across two dicts; (c) the new data-model deltas (`UpgradeRequest`, `PLANS`, `PREMIUM_QUOTAS`) and how Premium quotas merge with existing `used` values (AC-21 preserves them). |
| 9 | **NFR Requirements** | Minimal | Security considerations exist and are blocking (SEC-1..SEC-6). Tech stack is already fixed and no new dependency is permitted (NFR-1), so this stage only consolidates and sharpens what `requirements.md` already holds — minimal depth, not standard. It is required as input to stage 10 and to the architecture rubric. |
| 10 | **NFR Design** | Minimal | Follows stage 9. Defines *how* NFR-5 (all-or-nothing mutation) and SEC-2 (no cross-email read or mutation) are actually realised in code, rather than restating that they must be. |
| 11 | **`architecture.md` + rubrics + CI pipeline** | Always | At the STOP CHECKPOINT, automatic. Section 10 Verifiable Constraints mechanically derives `.evals/rubrics/architecture-rubric.json` — the blocking J1 gate. Also generates this project's `.github/workflows/agentic-eval-pipeline.yml` and `.spec/behavior.feature`. |
| 12 | 🛑 **STOP CHECKPOINT** | — | Hard halt. Code generation never starts on its own. |
| 13 | **Code Generation** (`dev-implement 1.1`) | — | User-driven. Story branch, Gherkin-first behaviour spec, code, then the full gate sequence. |

## 4. Recommended skips — 2 stages

### 🔵 PLANNING PHASE

| Stage | Rationale for skipping |
|---|---|
| **Reverse Engineering** | Atlas coverage is FULL (8 of 8 components, doc 3155 v28, CURRENT, human-reviewed). Per `common/helix-atlas-integration.md` Section 5 the stage is skipped and Atlas content becomes the artifacts. Re-deriving locally would produce a second, divergent source of truth — the exact failure the integration exists to prevent. **Saved**: a full-codebase analysis pass, and avoided a competing architecture document. |
| **Application Design** | No new components or services are introduced. The work adds functions and endpoints *inside* the existing `src/backend/main.py` module and extends the existing `Billing.jsx` component — changes within existing component boundaries. There is no service layer to design and no component-dependency question to clarify: the dependency graph in `knowledge-graph.md` already records every relationship, and the Epic specifies the exact function signature (`charge_card(email: str, amount: float) -> dict`) and both endpoint contracts. Component-level method and business-rule definition is genuinely needed, but it belongs in **Functional Design** (stage 8) where the open decisions actually live — running Application Design first would restate the Epic without resolving anything. |

### 🟢 IMPLEMENTATION PHASE

| Stage | Rationale for skipping |
|---|---|
| **Infrastructure Design** | Zero infrastructure delta. No new dependency (NFR-1, verified: `datetime` and Pydantic `BaseModel` are already imported). No new service, container, cloud resource, queue, or scheduled job. No deployment-topology change — the same `uvicorn main:app --port 8000` process plus the existing Vite dev proxy serve the two new routes with no configuration change. `architecture.md` will record this stage as explicitly skipped rather than filling its section with an invented decision. |

---

## 5. Package update sequence

Not applicable in the usual sense — this is a two-module repo, not a multi-package monorepo, and the
single story spans both modules. Within the story, the natural implementation order is:

1. **`src/backend/main.py`** — constants, `UpgradeRequest`, `charge_card()`, then `GET /api/billing/upgrade-preview`, then `POST /api/billing/upgrade` with its guards. The backend must exist first because AC-15 forbids the frontend from computing the amount, so the UI has nothing to render until the preview endpoint returns.
2. **`src/frontend/src/pages/Billing.jsx`** — dynamic plan render, CTA, modal, then success and failure handling.

## 6. Extensions in force

| Extension | Status | Effect on this plan |
|---|---|---|
| **Security Baseline** | ✅ mandatory, blocking | Diff-scoped automated security review inside Code Review. SEC-1..SEC-6 are hard constraints on the changed surface. The five pre-existing critical findings (email-as-token, plain-text passwords, wildcard CORS with credentials, credentials in query params, unpinned backend deps) are recorded as out-of-scope, not fixed. |
| **Playwright Test Automation** | ✅ mandatory | `/playwright-implement` runs after both the dev PR and the ve PR merge into the epic branch. The upgrade flow is UI-driven, so most ACs are automatable in the browser. |
| Resiliency Baseline | ❌ declined | — |
| Property-Based Testing | ❌ declined | Noted: the proration formula was the natural candidate. Its invariants (charge > 0, charge ≤ $20.00, `days_remaining` ≥ 1) will instead be asserted as ordinary unit tests per NFR-4. |

## 7. Parallel ve track

Independent of everything above and startable **now** — `/ve-implement 1.1` needs no dev branch, PR or
merge. This is where the second developer's capacity goes, given the single-story shape means the dev
track cannot be parallelised (R5 unmet).

## 8. Estimated timeline

| Phase | Estimate |
|---|---|
| Remaining design stages (8–10) | short — three focused stages, two at minimal depth |
| `architecture.md` + rubrics + CI pipeline (11) | one automatic pass |
| Code Generation for story 1.1 (13) | the Epic's own estimate for all five of its stories was ~3.5 days; as one automated `dev-implement` run it is a single long pass through the full gate sequence, with a 3-attempt self-healing budget per gate |
| ve track | parallel, startable immediately |

**Critical-path note**: the single-story shape means there is no dev-side parallelism to exploit and
one self-healing budget covers all 31 ACs. If a late gate fails repeatedly, the run halts with the
Retry-Limit Report and the whole story re-runs rather than one slice — the accepted consequence of the
recorded sizing deviation.
