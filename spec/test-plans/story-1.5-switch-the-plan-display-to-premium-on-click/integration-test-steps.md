# Integration Test Steps — story-1.5 Switch the plan display to Premium on click

**Purpose**: confirm the upgrade happens entirely in the browser (no request to the billing API) and keeps the renewal date that came from the API.
**Scope**: AC-1, AC-5.

## System Under Test
| Item | Value |
|------|-------|
| Branch | `epic/HELIX-7344-premium-upgrade-demo-frontend-only` |
| This story's PR | The `[STORY]` PR for Story 1.5, merged into the epic branch (TO CONFIRM: PR number once raised) |
| Confirm the story is in the build | `git log --oneline \| grep "1.5"` (TO CONFIRM: commit message pattern) |
| How to build & run it | **Follow the project's own build docs** (README / CONTRIBUTING). This plan does not restate them. |
| Local base URL / port | `http://localhost:5173` |
| Local services that must be up | FastAPI backend on port 8000, frontend dev server on port 5173 |
| Test data / accounts to seed | `tpg@example.com` / `password` |
| Tester tooling | Chrome DevTools Network panel ("Preserve log" on) and "Override content" |

### TC-INT-01 — No network request is sent when upgrading

| Field | Value |
|-------|-------|
| **Traces to** | AC-1 / REQ-F-03, REQ-NF-01 |
| **Type** | Integration |
| **Priority** | P1 |
| **Preconditions** | Signed in on the Billing page; DevTools Network tab open, filter "All", "Preserve log" on |
| **Test data** | None |

**Steps**
1. Reload the Billing page and wait for it to finish loading.
2. Clear the Network log.
3. Click **Upgrade to Premium**.
4. Wait 5 seconds and read the Network log.

**Expected result**
- The Network log is still empty: no XHR/fetch request, no document request, nothing to `/api/*`.
- The page shows Premium (see e2e-test-steps.md).

**Pass/Fail criteria**: PASS if no request at all appears after the click. Any request is a FAIL.
**Cleanup**: Reload the page.

### TC-INT-02 — "Renew at" keeps the API's date after the upgrade

| Field | Value |
|-------|-------|
| **Traces to** | AC-5 / REQ-F-08 |
| **Type** | Integration |
| **Priority** | P1 |
| **Preconditions** | Signed in as `tpg@example.com` on the Billing page |
| **Test data** | Expected date: "Oct 30, 2026" |

**Steps**
1. Read "Renew at" ("Oct 30, 2026").
2. Click **Upgrade to Premium**.
3. Read "Renew at" again.

**Expected result**
- "Renew at" still reads **Oct 30, 2026**.

**Pass/Fail criteria**: PASS if the date is unchanged. Anything else is a FAIL.
**Cleanup**: Reload the page.

### TC-INT-03 — "Renew at" is taken from the API, not hardcoded for Premium

| Field | Value |
|-------|-------|
| **Traces to** | AC-5 / REQ-F-08 |
| **Type** | Integration |
| **Priority** | P2 |
| **Preconditions** | As TC-INT-02, DevTools open |
| **Test data** | Override body: the real `/api/billing` response with `"renew_at": "Jan 15, 2027"` |

**Steps**
1. Override the `/api/billing` response body with `"renew_at": "Jan 15, 2027"` and reload the Billing page.
2. Confirm "Renew at" reads "Jan 15, 2027".
3. Click **Upgrade to Premium**.
4. Read "Renew at".

**Expected result**
- After the upgrade, "Renew at" still reads **Jan 15, 2027**.

**Pass/Fail criteria**: PASS if the overridden API date survives the upgrade. Any other date is a FAIL.
**Cleanup**: Remove the override and reload.
