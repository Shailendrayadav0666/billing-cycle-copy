# Integration Test Steps — story-1.2 Plan text follows the current plan

**Purpose**: confirm the boundary between the billing API response and the Billing page: the `plan_name` returned by `GET /api/billing` drives the badge and heading.
**Scope**: AC-1, AC-2. The backend always returns "Standard" for the demo account, so AC-2 is driven by overriding the response in the browser. No code is changed.

## System Under Test
| Item | Value |
|------|-------|
| Branch | `epic/HELIX-7344-premium-upgrade-demo-frontend-only` |
| This story's PR | The `[STORY]` PR for Story 1.2, merged into the epic branch (TO CONFIRM: PR number once raised) |
| Confirm the story is in the build | `git log --oneline \| grep "1.2"` (TO CONFIRM: commit message pattern) |
| How to build & run it | **Follow the project's own build docs** (README / CONTRIBUTING). This plan does not restate them. |
| Local base URL / port | `http://localhost:5173` (backend on `http://localhost:8000`, proxied) |
| Local services that must be up | FastAPI backend on port 8000, frontend dev server on port 5173 |
| Test data / accounts to seed | `tpg@example.com` / `password` |
| Tester tooling | Chrome DevTools "Override content" (Network panel > right-click the `/api/billing` request > Override content) |

### TC-INT-01 — Badge follows `plan_name` from the real API response

| Field | Value |
|-------|-------|
| **Traces to** | AC-1 / REQ-F-07 |
| **Type** | Integration |
| **Priority** | P1 |
| **Preconditions** | Signed in as `tpg@example.com`; DevTools Network tab open |
| **Test data** | None |

**Steps**
1. Reload the Billing page.
2. In DevTools > Network, select the `billing?email=...` request and open its Response tab.
3. Note the value of `plan_name`.
4. Compare it with the "Current plan" badge text on the page.

**Expected result**
- The response contains `"plan_name": "Standard"`.
- The badge text equals the `plan_name` value: **Standard**.

**Pass/Fail criteria**: PASS if the badge text equals the API's `plan_name`. Anything else is a FAIL.
**Cleanup**: None.

### TC-INT-02 — A Premium response shows Premium text in the Premium badge style

| Field | Value |
|-------|-------|
| **Traces to** | AC-2 / REQ-F-07, REQ-NF-03 |
| **Type** | Integration |
| **Priority** | P1 |
| **Preconditions** | As TC-INT-01; a screenshot of the Standard badge taken before this case for comparison |
| **Test data** | Override body: the real response with `"plan_name"` changed from `"Standard"` to `"Premium"` (all other fields unchanged) |

**Steps**
1. In DevTools > Network, right-click the `/api/billing` request and choose "Override content".
2. Edit the overridden body to set `"plan_name": "Premium"` and save it.
3. Reload the Billing page.
4. Read the "Current plan" badge and the section heading, and compare the badge's look with the Standard screenshot.

**Expected result**
- The badge reads **Premium**.
- The heading reads **What's included with Premium**.
- The badge is visibly styled differently from the Standard badge, for example a different colour (TO CONFIRM: the reference Premium style).

**Pass/Fail criteria**: PASS if both texts match and the badge style differs from Standard. Anything else is a FAIL.
**Cleanup**: In DevTools > Sources > Overrides, delete the override (or untick "Enable Local Overrides") and reload.

### TC-INT-03 — An unexpected plan name is shown as returned, not replaced

| Field | Value |
|-------|-------|
| **Traces to** | AC-2 / REQ-F-07 |
| **Type** | Integration |
| **Priority** | P3 |
| **Preconditions** | As TC-INT-02 |
| **Test data** | Override body with `"plan_name": "Basic"` |

**Steps**
1. Override the `/api/billing` response body with `"plan_name": "Basic"`.
2. Reload the Billing page.

**Expected result**
- The badge reads **Basic** and the heading reads **What's included with Basic**. The page does not fall back to the hardcoded word "Standard".

**Pass/Fail criteria**: PASS if the page shows the returned plan name in both places. Showing "Standard" anywhere in those two places is a FAIL.
**Cleanup**: Remove the override and reload.
