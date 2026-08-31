# Tech Stack Decisions — EPIC-1 Mid-Cycle Subscription Upgrade

**Depth**: Minimal
**Headline**: **no stack decision is open.** The stack is fixed, and NFR-1 forbids adding any
dependency. This document records that as a decision with reasons, rather than leaving the section
blank or inventing a choice nobody made.

---

## 1. Stack — inherited, unchanged

| Layer | Technology | Version | Decision |
|---|---|---|---|
| API framework | FastAPI | unpinned | **Keep.** Already serves all 6 endpoints; the 2 new ones are ordinary route handlers. |
| Validation | Pydantic | via FastAPI | **Keep.** `UpgradeRequest` is a plain `BaseModel`, same as the 3 existing request models. |
| ASGI server | uvicorn[standard] | unpinned | **Keep.** No change to the run command. |
| Date handling | `datetime` (stdlib) | — | **Keep.** Already imported at `main.py:6`. `strptime` covers the `renew_at` parse. |
| UI framework | React | ^19.2.8 | **Keep.** The modal and banner are plain function components with `useState`. |
| Routing | react-router-dom | ^7.18.2 | **Keep, unused by this change.** The modal deliberately does not navigate (AC-12). |
| Build | Vite | ^8.2.2 | **Keep.** Its existing `/api` proxy already covers both new routes with no config change. |
| Styling | plain CSS (`App.css`) | — | **Keep.** 8 new flat classes, no preprocessor, no CSS-in-JS, matching the file's convention. |
| Linting | Oxlint | ^1.79.0 | **Keep.** |

---

## 2. Decisions made *because* of the no-new-dependency constraint

Each of these is a place where a library would be the reflexive choice, and was declined:

| Temptation | Declined in favour of | Why |
|---|---|---|
| A money library (`Decimal`, `py-moneyed`) | Python `float` + `round(x, 2)` | Decision **D-1**. `Decimal` is stdlib so it costs no dependency, but it *does* contradict the Epic's explicitly specified formula. The exhaustive 30-value domain check makes float provably correct here. Reversal condition recorded in D-1. |
| A payment SDK (Stripe, Braintree) | In-repo `charge_card()` | The Epic's gateway spec is explicit: a deterministic in-repo dummy, no external service. Persona P3 depends on that determinism. |
| A modal library (Radix, Headless UI, MUI) | Local `UpgradeModal` in `Billing.jsx` | NFR-1. The modal is a conditional overlay div with two buttons; a library would add a dependency and a new styling system to a file using plain CSS. Accessibility is handled explicitly instead (`frontend-components.md` Section 7). |
| A fetch/state library (axios, TanStack Query, SWR) | Native `fetch` with `async/await` | NFR-1, and the file already uses native `fetch`. The new calls upgrade to `try/catch/finally` — better error handling than the existing `.then()` chains, with no dependency. |
| A schema/contract library beyond Pydantic | Pydantic alone | Already present via FastAPI; nothing more is needed for a one-field request model. |
| A date library (`arrow`, `pendulum`, `dateutil`) | stdlib `datetime` | Already imported. `strptime` with `"%b %d, %Y"` is exactly what the stored format needs. |

---

## 3. Testing stack — the one genuinely new choice

This is the only real decision in this document, because the repo has **zero tests** and therefore no
existing convention to inherit.

| Concern | Decision | Rationale |
|---|---|---|
| Backend unit tests | **pytest** + FastAPI's `TestClient` (`starlette.testclient`) | `TestClient` ships with FastAPI/Starlette, so it is already installed. pytest is the de facto Python standard and is what the AIRE eval scripts expect. |
| Backend test dependency | Added to a **dev/test** requirements path, never to `src/backend/requirements.txt` | NFR-1 forbids a new **runtime** dependency. A test-only dependency is not a runtime dependency, but it must not leak into the production manifest. |
| Gherkin execution | Per `common/behavior-spec.md`, run in **Podman** for the B1/B2/B3 tiers | Framework-mandated; not a free choice. |
| Frontend unit tests | **Deferred to the STOP CHECKPOINT** | The frontend has no test runner at all. Whether to add Vitest is a real decision, but it depends on the `.evals/config.json` thresholds that stage generates. Recorded as open rather than pre-empted here. |
| E2E / UI | **Playwright**, via the mandatory extension | Framework-mandated. Runs post-merge via `/playwright-implement`. |

**Note on `unitTestCoverageMin`**: the threshold is set in `.evals/config.json` at the STOP
CHECKPOINT. Because the repo starts at 0% coverage, coverage on the **changed surface** is the
meaningful measure, not whole-repo coverage — a whole-repo threshold would be unreachable in one
story regardless of how well this change is tested. Flagged for that stage to apply correctly.

---

## 4. Explicitly NOT decided here

| Deferred | To |
|---|---|
| Introducing a database | A separate cycle. Atlas rates the in-memory store as a critical architectural finding; replacing it is not this Epic. |
| Replacing email-as-token with JWT, hashing passwords, fixing CORS | A separate cycle. The Epic's ACs forbid auth changes. Recorded in `nfr-requirements.md` Section 6. |
| Pinning the backend dependencies | A separate cycle, though it is cheap and worth doing soon (Atlas 🟡 High). Out of this Epic's diff. |
| Splitting the `main.py` God module | A separate cycle. Adding two endpoints to a 212-line module does not itself justify a restructure, and restructuring would blow the regression baseline for a change with no user-visible benefit. |
| Adding TypeScript to the frontend | A separate cycle. |
| A frontend test runner (Vitest) | The STOP CHECKPOINT, once thresholds exist. |
