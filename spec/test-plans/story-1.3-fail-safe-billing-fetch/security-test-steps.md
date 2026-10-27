# Security Test Steps — story-1.3 Fail-safe billing fetch

**Purpose**: confirm a failed billing request discloses no internal detail to the user (Security Baseline SECURITY-15: generic user-facing errors, fail closed).
**Scope**: AC-3.

## System Under Test
| Item | Value |
|------|-------|
| Branch | `epic/HELIX-7344-premium-upgrade-demo-frontend-only` |
| This story's PR | The `[STORY]` PR for Story 1.3, merged into the epic branch (TO CONFIRM: PR number once raised) |
| Confirm the story is in the build | `git log --oneline \| grep "1.3"` (TO CONFIRM: commit message pattern) |
| How to build & run it | **Follow the project's own build docs** (README / CONTRIBUTING). This plan does not restate them. |
| Local base URL / port | `http://localhost:5173` |
| Local services that must be up | FastAPI backend on port 8000, frontend dev server on port 5173 |
| Test data / accounts to seed | `tpg@example.com` / `password` |
| Tester tooling | Request-rewriting tool as in integration-test-steps.md (TO CONFIRM: tool); Chrome DevTools |

### TC-SEC-01 — 401 detail is not shown on the page

| Field | Value |
|-------|-------|
| **Traces to** | AC-3 / REQ-NF-08, SECURITY-15 |
| **Type** | Security |
| **Priority** | P1 |
| **Preconditions** | Signed in as `tpg@example.com`; rewrite rule answering `/api/billing` with status 401 and body `{"detail": "Not authenticated"}` |
| **Test data** | Search strings: `401`, `Not authenticated`, `detail`, `Error`, `at ` (stack frame prefix) |

**Steps**
1. Enable the 401 rewrite rule and reload the Billing page.
2. Use the browser's Find (Ctrl+F) to search the page for each search string.

**Expected result**
- None of the search strings is found in the visible page content (the navigation's own labels excepted).
- The only content-area text is **Loading billing...**.

**Pass/Fail criteria**: PASS if no status code, response body text or stack trace is visible. Any match is a FAIL.
**Cleanup**: Disable the rewrite rule and reload.

### TC-SEC-02 — Network error message is not shown on the page

| Field | Value |
|-------|-------|
| **Traces to** | AC-3 / REQ-NF-08, SECURITY-15 |
| **Type** | Security |
| **Priority** | P2 |
| **Preconditions** | Signed in as `tpg@example.com`; DevTools request blocking active for `*/api/billing*` |
| **Test data** | Search strings: `Failed to fetch`, `TypeError`, `ERR_`, `NetworkError` |

**Steps**
1. Reload the Billing page with blocking active.
2. Search the visible page for each search string.

**Expected result**
- None of the search strings is visible on the page. The content area shows only **Loading billing...**.

**Pass/Fail criteria**: PASS if no error text is visible. Any match is a FAIL.
**Cleanup**: Remove the blocking pattern and reload.
