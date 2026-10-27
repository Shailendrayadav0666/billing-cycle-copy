# E2E Test Steps — story-1.4 Upgrade button on the Standard plan

**Purpose**: confirm a Standard subscriber sees the "Upgrade to Premium" call to action in the right place.
**Scope**: AC-1.

## System Under Test
| Item | Value |
|------|-------|
| Branch | `epic/HELIX-7344-premium-upgrade-demo-frontend-only` |
| This story's PR | The `[STORY]` PR for Story 1.4, merged into the epic branch (TO CONFIRM: PR number once raised) |
| Confirm the story is in the build | `git log --oneline \| grep "1.4"` (TO CONFIRM: commit message pattern) |
| How to build & run it | **Follow the project's own build docs** (README / CONTRIBUTING). This plan does not restate them. |
| Local base URL / port | `http://localhost:5173` (backend on `http://localhost:8000`, proxied) |
| Local services that must be up | FastAPI backend on port 8000, frontend dev server on port 5173 |
| Test data / accounts to seed | `tpg@example.com` / `password` (Standard plan) |

> If the build or local run fails, that is a **blocker on the dev team**. Report it and do not log functional failures against a system that never started.

### TC-E2E-01 — Standard subscriber sees the Upgrade button

| Field | Value |
|-------|-------|
| **Traces to** | AC-1 / REQ-F-01 |
| **Type** | E2E |
| **Priority** | P1 |
| **Preconditions** | System Under Test running; no stored session |
| **Test data** | `tpg@example.com` / `password` |

**Steps**
1. Open `http://localhost:5173` and sign in as `tpg@example.com` / `password`.
2. Open the Billing page.

**Expected result**
- A button labelled exactly **Upgrade to Premium** is visible.
- Exactly one such button is on the page.

**Pass/Fail criteria**: PASS if exactly one "Upgrade to Premium" button is visible. Anything else is a FAIL.
**Cleanup**: None.

### TC-E2E-02 — The button sits in the header row, aligned right

| Field | Value |
|-------|-------|
| **Traces to** | AC-1 / REQ-F-01, REQ-NF-03 |
| **Type** | E2E |
| **Priority** | P2 |
| **Preconditions** | As TC-E2E-01, on the Billing page; browser window 1280 px wide |
| **Test data** | Window widths: 1280 px, then 768 px |

**Steps**
1. At 1280 px wide, look at the page header that holds "Plan & Billing" and "Manage your plan and payments".
2. Resize the window to 768 px wide and look again.

**Expected result**
- At 1280 px, the button is on the same row as the "Plan & Billing" title, at the right-hand end of that row.
- At 768 px, the button stays fully visible and does not overlap the title or subtitle text.

**Pass/Fail criteria**: PASS if the placement is as described at 1280 px and nothing overlaps at 768 px. Anything else is a FAIL.
**Cleanup**: Restore the window size.
