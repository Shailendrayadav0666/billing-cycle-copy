# Integration Test Steps — story-1.4 Upgrade button on the Standard plan

**Purpose**: confirm the button's visibility rule at the boundary with the billing API. The button shows only when `plan_name` from `GET /api/billing` is exactly "Standard".
**Scope**: AC-2. The demo account always returns "Standard", so the other values are produced by overriding the response body in the browser. No code is changed.

## System Under Test
| Item | Value |
|------|-------|
| Branch | `epic/HELIX-7344-premium-upgrade-demo-frontend-only` |
| This story's PR | The `[STORY]` PR for Story 1.4, merged into the epic branch (TO CONFIRM: PR number once raised) |
| Confirm the story is in the build | `git log --oneline \| grep "1.4"` (TO CONFIRM: commit message pattern) |
| How to build & run it | **Follow the project's own build docs** (README / CONTRIBUTING). This plan does not restate them. |
| Local base URL / port | `http://localhost:5173` |
| Local services that must be up | FastAPI backend on port 8000, frontend dev server on port 5173 |
| Test data / accounts to seed | `tpg@example.com` / `password` |
| Tester tooling | Chrome DevTools "Override content" and network throttling |

### TC-INT-01 — No button when the plan is "Premium"

| Field | Value |
|-------|-------|
| **Traces to** | AC-2 / REQ-F-02 |
| **Type** | Integration |
| **Priority** | P1 |
| **Preconditions** | Signed in as `tpg@example.com`; DevTools open |
| **Test data** | Override body: real response with `"plan_name": "Premium"` |

**Steps**
1. Override the `/api/billing` response body with `"plan_name": "Premium"`.
2. Reload the Billing page.

**Expected result**
- No "Upgrade to Premium" button is anywhere on the page.

**Pass/Fail criteria**: PASS if the button is absent. Any visible "Upgrade to Premium" button is a FAIL.
**Cleanup**: Remove the override and reload.

### TC-INT-02 — No button when the plan name differs only in case

| Field | Value |
|-------|-------|
| **Traces to** | AC-2 / REQ-F-02 |
| **Type** | Integration |
| **Priority** | P2 |
| **Preconditions** | As TC-INT-01 |
| **Test data** | Override bodies: `"plan_name": "standard"`, then `"plan_name": "Standard "` (with a trailing space) |

**Steps**
1. Override the response with `"plan_name": "standard"` and reload the Billing page.
2. Override the response with `"plan_name": "Standard "` and reload again.

**Expected result**
- In both cases no "Upgrade to Premium" button is shown.

**Pass/Fail criteria**: PASS if the button is absent both times. Showing the button for either value is a FAIL.
**Cleanup**: Remove the override and reload.

### TC-INT-03 — No button while billing is still loading

| Field | Value |
|-------|-------|
| **Traces to** | AC-2 / REQ-F-02 |
| **Type** | Integration |
| **Priority** | P3 |
| **Preconditions** | Signed in as `tpg@example.com`; no overrides |
| **Test data** | DevTools throttling "Slow 3G" |

**Steps**
1. Set DevTools network throttling to "Slow 3G".
2. Reload the Billing page and watch it before `/api/billing` completes.
3. Wait for the response to arrive.

**Expected result**
- While "Loading billing..." is shown, no "Upgrade to Premium" button is visible.
- Once the Standard response arrives, the button appears.

**Pass/Fail criteria**: PASS if the button appears only after the Standard response has loaded. Anything else is a FAIL.
**Cleanup**: Set throttling back to "No throttling".
