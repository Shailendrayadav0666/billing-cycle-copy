# E2E Test Steps — story-1.5 Switch the plan display to Premium on click

**Purpose**: confirm a Standard subscriber who clicks "Upgrade to Premium" sees the whole plan display switch to the Premium values.
**Scope**: AC-1 to AC-4.

## System Under Test
| Item | Value |
|------|-------|
| Branch | `epic/HELIX-7344-premium-upgrade-demo-frontend-only` |
| This story's PR | The `[STORY]` PR for Story 1.5, merged into the epic branch; Stories 1.2 and 1.4 are already merged (prerequisites) (TO CONFIRM: PR number once raised) |
| Confirm the story is in the build | `git log --oneline \| grep "1.5"` (TO CONFIRM: commit message pattern) |
| How to build & run it | **Follow the project's own build docs** (README / CONTRIBUTING). This plan does not restate them. |
| Local base URL / port | `http://localhost:5173` (backend on `http://localhost:8000`, proxied) |
| Local services that must be up | FastAPI backend on port 8000, frontend dev server on port 5173 |
| Test data / accounts to seed | `tpg@example.com` / `password` (Standard, "$20/month", renew "Oct 30, 2026") |

> If the build or local run fails, that is a **blocker on the dev team**. Report it and do not log functional failures against a system that never started.

### TC-E2E-01 — Click switches the badge and heading to Premium

| Field | Value |
|-------|-------|
| **Traces to** | AC-1 / REQ-F-03 |
| **Type** | E2E |
| **Priority** | P1 |
| **Preconditions** | Signed in as `tpg@example.com` on the Billing page showing Standard |
| **Test data** | None |

**Steps**
1. Confirm the badge reads "Standard".
2. Click **Upgrade to Premium**.
3. Read the badge and the section heading immediately.

**Expected result**
- The badge reads **Premium** and the heading reads **What's included with Premium** straight after the click, with no loading state in between.
- No confirmation dialog or modal appears.
- The browser does not reload the page: the address bar and history do not change.

**Pass/Fail criteria**: PASS if the switch is immediate with no dialog and no reload. Anything else is a FAIL.
**Cleanup**: Reload the page (this returns it to Standard).

### TC-E2E-02 — Price switches to $25/month

| Field | Value |
|-------|-------|
| **Traces to** | AC-2 / REQ-F-04 |
| **Type** | E2E |
| **Priority** | P1 |
| **Preconditions** | As TC-E2E-01 |
| **Test data** | None |

**Steps**
1. Note the plan card price ("$20/month").
2. Click **Upgrade to Premium**.
3. Read the plan card price.

**Expected result**
- The price reads exactly **$25/month**. "$20/month" no longer appears anywhere on the page.

**Pass/Fail criteria**: PASS if the price is exactly "$25/month". Anything else is a FAIL.
**Cleanup**: Reload the page.

### TC-E2E-03 — Usage cards switch to the Premium values

| Field | Value |
|-------|-------|
| **Traces to** | AC-3 / REQ-F-05 |
| **Type** | E2E |
| **Priority** | P1 |
| **Preconditions** | As TC-E2E-01; a screenshot of the Standard usage cards taken before clicking |
| **Test data** | Expected values below |

**Steps**
1. Click **Upgrade to Premium**.
2. Read the three usage cards from left to right.
3. Hover over each card to show its tooltip, and read it.
4. Compare the card icons and order with the Standard screenshot.

**Expected result**
- Order and icons are unchanged: "Video quality", "Watch at the same time", "Download on devices".
- "Video quality" shows **4K Ultra HD + HDR**; its tooltip reads **The best video resolution available on the Premium plan.**
- "Watch at the same time" shows **Can watch on 4 devices at once**; its tooltip still reads "Number of supported devices that can stream on your account simultaneously."
- "Download on devices" shows **Can download on 6 devices**; its tooltip still reads "Number of supported devices you can download titles to for offline viewing."

**Pass/Fail criteria**: PASS if every value, tooltip, icon and the order match. Any mismatch is a FAIL.
**Cleanup**: Reload the page.

### TC-E2E-04 — Plan perks switch to the Premium perks

| Field | Value |
|-------|-------|
| **Traces to** | AC-4 / REQ-F-06 |
| **Type** | E2E |
| **Priority** | P1 |
| **Preconditions** | As TC-E2E-01 |
| **Test data** | Expected values below |

**Steps**
1. Click **Upgrade to Premium**.
2. Read the "Plan perks" card, then hover its info icon to read its help text (TO CONFIRM: where the help text is shown, if it is not on the info icon).

**Expected result**
- The card lists exactly three perks: **Ad-free streaming**, **Spatial audio (select titles)**, **Dolby Atmos (select titles)**.
- Each perk shows **100% used** with a full progress bar.
- The help text reads **Perks included in your Premium plan.**

**Pass/Fail criteria**: PASS if the three perks, their 100% values and the help text match. Anything else is a FAIL.
**Cleanup**: Reload the page.
