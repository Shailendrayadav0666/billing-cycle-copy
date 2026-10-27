# E2E Test Steps — story-1.2 Plan text follows the current plan

**Purpose**: confirm, through the real UI, that the Billing page's plan text comes from the subscriber's actual plan and that nothing else on the page changed.
**Scope**: AC-1, AC-3, AC-4.

## System Under Test
| Item | Value |
|------|-------|
| Branch | `epic/HELIX-7344-premium-upgrade-demo-frontend-only` |
| This story's PR | The `[STORY]` PR for Story 1.2, merged into the epic branch (TO CONFIRM: PR number once raised) |
| Confirm the story is in the build | `git log --oneline \| grep "1.2"` (TO CONFIRM: commit message pattern) |
| How to build & run it | **Follow the project's own build docs** (README / CONTRIBUTING). This plan does not restate them. |
| Local base URL / port | `http://localhost:5173` (frontend dev server; `/api/*` is proxied to the backend on `http://localhost:8000`, per spec/plans/atlas-deep-dive.md Getting Started) |
| Local services that must be up | FastAPI backend on port 8000, frontend dev server on port 5173 |
| Test data / accounts to seed | Pre-seeded demo account `tpg@example.com` / `password` (Standard plan, price "$20/month", renew date "Oct 30, 2026") |

> If the build or local run fails, that is a **blocker on the dev team**. Report it and do not log functional failures against a system that never started.

### TC-E2E-01 — Standard subscriber sees Standard plan text

| Field | Value |
|-------|-------|
| **Traces to** | AC-1 / REQ-F-07 |
| **Type** | E2E |
| **Priority** | P1 |
| **Preconditions** | System Under Test running; browser with no stored session (clear site data for `localhost:5173`) |
| **Test data** | `tpg@example.com` / `password` |

**Steps**
1. Open `http://localhost:5173` and sign in as `tpg@example.com` / `password`.
2. Open the Billing page.
3. Read the "Current plan" line and the section heading above the usage cards.

**Expected result**
- The "Current plan" badge reads **Standard**.
- The section heading reads **What's included with Standard**.

**Pass/Fail criteria**: PASS if both texts match exactly. Anything else is a FAIL.
**Cleanup**: Sign out.

### TC-E2E-02 — The rest of the page is unchanged

| Field | Value |
|-------|-------|
| **Traces to** | AC-3 / REQ-F-12 |
| **Type** | E2E |
| **Priority** | P2 |
| **Preconditions** | Signed in as `tpg@example.com` on the Billing page |
| **Test data** | Expected texts below |

**Steps**
1. On the Billing page, read the page title area, the plan card and the copy under "Current plan".

**Expected result**
- The page title reads "Plan & Billing" and the subtitle reads "Manage your plan and payments".
- The plan card label reads "Monthly plan" and shows the "Active" badge.
- The copy under "Current plan" reads "Unlimited movies, TV shows and more. Watch anywhere. Cancel anytime."
- The price reads "$20/month" and "Renew at" reads "Oct 30, 2026".

**Pass/Fail criteria**: PASS if every text matches exactly. Any missing or changed text is a FAIL.
**Cleanup**: None.

### TC-E2E-03 — Loading state while the billing response is pending

| Field | Value |
|-------|-------|
| **Traces to** | AC-4 / REQ-F-12 |
| **Type** | E2E |
| **Priority** | P3 |
| **Preconditions** | Signed in as `tpg@example.com`; Chrome DevTools open on the Network tab |
| **Test data** | DevTools network throttling profile "Slow 3G" (or a custom profile with a 5 s latency) |

**Steps**
1. In DevTools > Network, set throttling to "Slow 3G".
2. Reload the Billing page.
3. Watch the page before the `/api/billing` request completes.

**Expected result**
- While the request is pending, the page shows **Loading billing...**.
- No "Current plan" badge and no plan heading appear until the response arrives.

**Pass/Fail criteria**: PASS if the loading text shows and no plan text appears while pending. Anything else is a FAIL.
**Cleanup**: Set throttling back to "No throttling".
