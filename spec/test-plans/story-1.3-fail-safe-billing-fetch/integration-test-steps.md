# Integration Test Steps — story-1.3 Fail-safe billing fetch

**Purpose**: confirm the Billing page handles a failed `GET /api/billing` safely, both a request that never completes and a non-OK response.
**Scope**: AC-1, AC-2.

## System Under Test
| Item | Value |
|------|-------|
| Branch | `epic/HELIX-7344-premium-upgrade-demo-frontend-only` |
| This story's PR | The `[STORY]` PR for Story 1.3, merged into the epic branch (TO CONFIRM: PR number once raised) |
| Confirm the story is in the build | `git log --oneline \| grep "1.3"` (TO CONFIRM: commit message pattern) |
| How to build & run it | **Follow the project's own build docs** (README / CONTRIBUTING). This plan does not restate them. |
| Local base URL / port | `http://localhost:5173` (backend on `http://localhost:8000`, proxied) |
| Local services that must be up | FastAPI backend on port 8000, frontend dev server on port 5173 |
| Test data / accounts to seed | `tpg@example.com` / `password` |
| Tester tooling | Chrome DevTools (Network request blocking, Console); a local request-rewriting tool able to set a response status for one URL (TO CONFIRM: team's preferred tool, for example Requestly or mitmproxy) |

> If the build or local run fails, that is a **blocker on the dev team**. Report it and do not log functional failures against a system that never started.

### TC-INT-01 — Network failure: no unhandled rejection, page stays on loading

| Field | Value |
|-------|-------|
| **Traces to** | AC-1 / REQ-NF-08 |
| **Type** | Integration |
| **Priority** | P1 |
| **Preconditions** | Signed in as `tpg@example.com`; DevTools open with the Console cleared and "Preserve log" on |
| **Test data** | Blocked URL pattern: `*/api/billing*` |

**Steps**
1. In DevTools, open the "Network request blocking" panel and add the pattern `*/api/billing*`. Enable blocking.
2. Reload the Billing page.
3. Wait 10 seconds.
4. Read the page, and read the Console.

**Expected result**
- The page shows **Loading billing...** and nothing else in the content area.
- The Console shows the blocked request (`net::ERR_BLOCKED_BY_CLIENT`) but **no** "Uncaught (in promise)" error.
- The page is still responsive: the header and navigation still work.

**Pass/Fail criteria**: PASS if the loading text stays and no "Uncaught (in promise)" error appears. A blank page, a crash, or an uncaught rejection is a FAIL.
**Cleanup**: Remove the blocking pattern and reload.

### TC-INT-02 — 401 response is not used as billing data

| Field | Value |
|-------|-------|
| **Traces to** | AC-2 / REQ-NF-08 |
| **Type** | Integration |
| **Priority** | P1 |
| **Preconditions** | Signed in as `tpg@example.com`; request-rewriting tool set to answer `GET /api/billing` with status 401 and body `{"detail": "Not authenticated"}` (TO CONFIRM: tool) |
| **Test data** | Status 401, body `{"detail": "Not authenticated"}` |

**Steps**
1. Enable the 401 rewrite rule for `/api/billing`.
2. Reload the Billing page.
3. Wait 10 seconds and read the page and the Console.

**Expected result**
- The page shows **Loading billing...**.
- No "Current plan" badge, price, usage card or perks card is shown.
- The page does not go blank, and the Console shows no uncaught `TypeError` (for example "Cannot read properties of undefined").

**Pass/Fail criteria**: PASS if the page stays on the loading text with no crash. A blank page, partly rendered plan data, or an uncaught error is a FAIL.
**Cleanup**: Disable the rewrite rule and reload.

### TC-INT-03 — 500 response is not used as billing data

| Field | Value |
|-------|-------|
| **Traces to** | AC-2 / REQ-NF-08 |
| **Type** | Integration |
| **Priority** | P2 |
| **Preconditions** | As TC-INT-02, with the rewrite rule set to status 500 and body `{"detail": "Internal Server Error"}` |
| **Test data** | Status 500 |

**Steps**
1. Enable the 500 rewrite rule for `/api/billing`.
2. Reload the Billing page and wait 10 seconds.

**Expected result**
- The page shows **Loading billing...** with no plan data and no crash.

**Pass/Fail criteria**: PASS if the page stays on the loading text with no crash. Anything else is a FAIL.
**Cleanup**: Disable the rewrite rule and reload.

### TC-INT-04 — A successful response still renders the page

| Field | Value |
|-------|-------|
| **Traces to** | AC-1 / REQ-NF-08 (regression guard) |
| **Type** | Integration |
| **Priority** | P1 |
| **Preconditions** | Signed in as `tpg@example.com`; no blocking or rewrite rules active |
| **Test data** | None |

**Steps**
1. Reload the Billing page.

**Expected result**
- The page renders the plan with price **$20/month** and "Renew at" **Oct 30, 2026**, the three usage cards and the "Plan perks" card.

**Pass/Fail criteria**: PASS if the normal page renders fully. A loading text that never resolves on a healthy API is a FAIL.
**Cleanup**: None.
