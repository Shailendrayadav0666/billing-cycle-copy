# Security Test Steps — story-1.5 Switch the plan display to Premium on click

**Purpose**: confirm the upgrade is cosmetic. Nothing is persisted in the browser and no real plan changes on the server (REQ-NF-09, Security Baseline SECURITY-11 misuse consideration).
**Scope**: AC-1 (no storage write, no server-side effect).

## System Under Test
| Item | Value |
|------|-------|
| Branch | `epic/HELIX-7344-premium-upgrade-demo-frontend-only` |
| This story's PR | The `[STORY]` PR for Story 1.5, merged into the epic branch (TO CONFIRM: PR number once raised) |
| Confirm the story is in the build | `git log --oneline \| grep "1.5"` (TO CONFIRM: commit message pattern) |
| How to build & run it | **Follow the project's own build docs** (README / CONTRIBUTING). This plan does not restate them. |
| Local base URL / port | `http://localhost:5173`; backend API directly at `http://localhost:8000` |
| Local services that must be up | FastAPI backend on port 8000, frontend dev server on port 5173 |
| Test data / accounts to seed | `tpg@example.com` / `password` |
| Tester tooling | Chrome DevTools Application panel; `curl` |

### TC-SEC-01 — Nothing about the upgrade is written to browser storage

| Field | Value |
|-------|-------|
| **Traces to** | AC-1 / REQ-NF-09, REQ-F-11 |
| **Type** | Security |
| **Priority** | P1 |
| **Preconditions** | Signed in on the Billing page; DevTools > Application open |
| **Test data** | None |

**Steps**
1. In Application > Local Storage, Session Storage, Cookies and IndexedDB for `http://localhost:5173`, note every key that exists (the sign-in token is expected).
2. Click **Upgrade to Premium**.
3. Refresh the Application panel views and compare.

**Expected result**
- No key was added or changed. No value contains "Premium", "plan", "upgrade" or "$25".

**Pass/Fail criteria**: PASS if browser storage is identical before and after the click. Any new or changed entry is a FAIL.
**Cleanup**: Reload the page.

### TC-SEC-02 — The server-side plan is unchanged after the upgrade

| Field | Value |
|-------|-------|
| **Traces to** | AC-1 / REQ-NF-09, REQ-NF-01 |
| **Type** | Security |
| **Priority** | P1 |
| **Preconditions** | As TC-SEC-01 |
| **Test data** | `curl "http://localhost:8000/api/billing?email=tpg%40example.com"` |

**Steps**
1. Click **Upgrade to Premium** in the browser and confirm the page shows Premium.
2. In a terminal, run `curl "http://localhost:8000/api/billing?email=tpg%40example.com"`.

**Expected result**
- The API response still contains `"plan_name":"Standard"` and `"price":"$20/month"`. The demo upgrade granted nothing on the server.

**Pass/Fail criteria**: PASS if the API still reports Standard. Any change to the server-side plan is a FAIL.
**Cleanup**: Reload the browser page.
