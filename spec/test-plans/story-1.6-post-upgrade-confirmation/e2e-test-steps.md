# E2E Test Steps — story-1.6 Post-upgrade confirmation

**Purpose**: confirm the subscriber gets a clear, lasting confirmation after upgrading, that the button goes away, and that a reload resets the demo.
**Scope**: AC-1, AC-3, AC-4, AC-5.

## System Under Test
| Item | Value |
|------|-------|
| Branch | `epic/HELIX-7344-premium-upgrade-demo-frontend-only` |
| This story's PR | The `[STORY]` PR for Story 1.6, merged into the epic branch; Story 1.5 is already merged (prerequisite) (TO CONFIRM: PR number once raised) |
| Confirm the story is in the build | `git log --oneline \| grep "1.6"` (TO CONFIRM: commit message pattern) |
| How to build & run it | **Follow the project's own build docs** (README / CONTRIBUTING). This plan does not restate them. |
| Local base URL / port | `http://localhost:5173` (backend on `http://localhost:8000`, proxied) |
| Local services that must be up | FastAPI backend on port 8000, frontend dev server on port 5173 |
| Test data / accounts to seed | `tpg@example.com` / `password` (Standard plan) |

> If the build or local run fails, that is a **blocker on the dev team**. Report it and do not log functional failures against a system that never started.

### TC-E2E-01 — Success banner appears with the exact text

| Field | Value |
|-------|-------|
| **Traces to** | AC-1 / REQ-F-09 |
| **Type** | E2E |
| **Priority** | P1 |
| **Preconditions** | Signed in as `tpg@example.com` on the Billing page showing Standard |
| **Test data** | Expected text: `You're now on Premium! Enjoy 4K Ultra HD, more screens and more downloads.` |

**Steps**
1. Click **Upgrade to Premium**.
2. Read the banner at the top of the Billing page content.

**Expected result**
- A success banner appears at the top of the Billing page, above the plan details.
- Its text is exactly **You're now on Premium! Enjoy 4K Ultra HD, more screens and more downloads.** Punctuation, the apostrophe and capitalisation all match.

**Pass/Fail criteria**: PASS if the banner appears at the top with exactly this text. Anything else is a FAIL.
**Cleanup**: Reload the page.

### TC-E2E-02 — No banner before the upgrade

| Field | Value |
|-------|-------|
| **Traces to** | AC-1 / REQ-F-09 |
| **Type** | E2E |
| **Priority** | P2 |
| **Preconditions** | Signed in as `tpg@example.com`; Billing page freshly loaded |
| **Test data** | None |

**Steps**
1. Load the Billing page and do not click anything.
2. Look for any success banner.

**Expected result**
- No success banner is shown. The text "You're now on Premium!" is not on the page.

**Pass/Fail criteria**: PASS if no banner is shown before the click. FAIL otherwise.
**Cleanup**: None.

### TC-E2E-03 — Banner stays and cannot be dismissed

| Field | Value |
|-------|-------|
| **Traces to** | AC-3 / REQ-F-09 |
| **Type** | E2E |
| **Priority** | P2 |
| **Preconditions** | As TC-E2E-01 |
| **Test data** | Wait time: 30 seconds |

**Steps**
1. Click **Upgrade to Premium**.
2. Look for a close (x) or dismiss control on the banner.
3. Wait 30 seconds without touching the page.
4. Hover over and scroll through the usage cards, then scroll back to the top.

**Expected result**
- The banner has no close or dismiss control.
- After 30 seconds and the interactions, the banner is still visible with the same text.

**Pass/Fail criteria**: PASS if the banner has no dismiss control and is still shown at the end. Anything else is a FAIL.
**Cleanup**: Reload the page.

### TC-E2E-04 — Upgrade button disappears after upgrading

| Field | Value |
|-------|-------|
| **Traces to** | AC-4 / REQ-F-10 |
| **Type** | E2E |
| **Priority** | P1 |
| **Preconditions** | As TC-E2E-01 |
| **Test data** | None |

**Steps**
1. Confirm the **Upgrade to Premium** button is visible.
2. Click it.
3. Search the page (Ctrl+F) for "Upgrade to Premium".

**Expected result**
- After the click, no "Upgrade to Premium" button is on the page, and the search finds no button with that label.

**Pass/Fail criteria**: PASS if the button is gone after the upgrade. A remaining or disabled-but-visible button is a FAIL.
**Cleanup**: Reload the page.

### TC-E2E-05 — Reload resets the page to Standard

| Field | Value |
|-------|-------|
| **Traces to** | AC-5 / REQ-F-11 |
| **Type** | E2E |
| **Priority** | P1 |
| **Preconditions** | As TC-E2E-01; DevTools Network tab open with "Preserve log" on |
| **Test data** | None |

**Steps**
1. Click **Upgrade to Premium** and confirm the page shows Premium with the banner.
2. Clear the Network log.
3. Reload the page (F5).
4. Read the Network log and the page.
5. Navigate away to another page of the app, then back to the Billing page.

**Expected result**
- After the reload, the Network log shows a new `/api/billing` request.
- The badge reads **Standard**, the price reads **$20/month**, the **Upgrade to Premium** button is shown, and no success banner is shown.
- After navigating away and back, the page again shows Standard with the button and no banner.

**Pass/Fail criteria**: PASS if both reload and revisit return the page to Standard with the button and no banner. Anything else is a FAIL.
**Cleanup**: None.
