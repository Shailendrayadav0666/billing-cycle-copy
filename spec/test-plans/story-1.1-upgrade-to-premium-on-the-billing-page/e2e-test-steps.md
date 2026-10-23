# E2E Test Steps: Story 1.1 Upgrade to Premium on the Billing page (frontend only)

**Purpose**: verify the complete user journey on the Billing page, from login to upgrade confirmation, as a human sees it in the browser.
**Scope**: AC-1, AC-2, AC-3, AC-4, AC-5, AC-6, AC-7 (reload), AC-9 (display unchanged).
**Derived from**: `spec/plans/stories.md` Story 1.1 acceptance criteria, `spec/plans/requirements.md` v1. No application source code was read.

## System Under Test
| Item | Value |
|------|-------|
| Branch | `epic/7344-premium-upgrade-demo-frontend-only` |
| This story's PR | TO CONFIRM: the `[STORY]` PR for Story 1.1, which must be MERGED into the epic branch before execution |
| Confirm the story is in the build | `git log --oneline \| grep -i "1.1"` (the Story 1.1 merge commit is present) |
| How to build & run it | **Follow the project's own build docs** (README / CONTRIBUTING / Makefile). This plan does not restate them. |
| Local base URL / port | Frontend dev server `http://localhost:5173`, which proxies `/api/*` to the backend on `http://localhost:8000` (Atlas deep dive, Getting Started) |
| Local services that must be up | Backend API on port 8000 and the frontend dev server on port 5173 |
| Test data / accounts to seed | None to seed. Use the built-in demo user `tpg@example.com` / `password` (Standard plan, $20/month, renews Oct 30, 2026). A freshly registered user also starts on Standard. |

> If the build or local run fails, that is a **blocker on the dev team**. Report it and do not log functional failures against a system that never started.

Browser: any current Chromium, Firefox or Safari, at a desktop window width.

---

### TC-E2E-01: Standard user sees the "Upgrade to Premium" button below the plan row

| Field | Value |
|-------|-------|
| **Traces to** | AC-1 / REQ-F-01, REQ-F-08 |
| **Type** | E2E |
| **Priority** | P1 |
| **Preconditions** | System Under Test running; backend freshly started so the demo user is on Standard |
| **Test data** | `tpg@example.com` / `password` |

**Steps**
1. Open `http://localhost:5173` and log in with the test data.
2. Click **Billing** in the top bar if you are not already on the Billing page.
3. Wait until the "Loading billing..." text is replaced by the plan details.
4. Look at the area between the plan row (the "Monthly plan" card and the "Renew at" card) and the "What's included with ..." heading.

**Expected result**
- A button labelled exactly **Upgrade to Premium** is visible.
- It appears below the plan card and Renew at card, and above the "What's included with Standard" heading.
- The button is only about as wide as its label (it does NOT stretch across the whole card) and sits at the left.
- It uses the same teal colour as the other primary buttons in the app (for example the login button), and darkens on hover.

**Pass/Fail criteria**: PASS if every expected result holds. Otherwise FAIL.
**Cleanup**: none (no state changed).

### TC-E2E-02: The button is not shown while billing is still loading

| Field | Value |
|-------|-------|
| **Traces to** | AC-2 / REQ-F-02 |
| **Type** | E2E |
| **Priority** | P3 |
| **Preconditions** | Logged in as the test user. Browser DevTools available. |
| **Test data** | DevTools Network throttling: "Slow 3G" |

**Steps**
1. Open DevTools, then Network, and set throttling to **Slow 3G**.
2. Reload the Billing page.
3. While "Loading billing..." is displayed, look for an Upgrade to Premium button.
4. Reset throttling to "No throttling".

**Expected result**
- While "Loading billing..." is shown, no Upgrade to Premium button is visible.
- After loading completes, the button appears (as in TC-E2E-01).

**Pass/Fail criteria**: PASS if the button never appears during the loading state.
**Cleanup**: set throttling back to "No throttling".

### TC-E2E-03: Plan badge and heading show the current plan from the data

| Field | Value |
|-------|-------|
| **Traces to** | AC-3 / REQ-F-05, REQ-F-09 |
| **Type** | E2E |
| **Priority** | P1 |
| **Preconditions** | Logged in as the Standard test user, on the Billing page, with no upgrade clicked yet |
| **Test data** | `tpg@example.com` / `password` |

**Steps**
1. Read the badge next to the text "Current plan:".
2. Read the heading above the usage cards.
3. Note the badge's colours (teal text on a light teal background, with a teal border).

**Expected result**
- The badge reads **Standard**.
- The heading reads **What's included with Standard**.
- The badge keeps its existing teal styling.

**Pass/Fail criteria**: PASS if all three hold.
**Cleanup**: none.

### TC-E2E-04: Clicking upgrade switches all plan details to Premium without a reload

| Field | Value |
|-------|-------|
| **Traces to** | AC-4, AC-5 / REQ-F-03, REQ-F-04 |
| **Type** | E2E |
| **Priority** | P1 |
| **Preconditions** | Logged in as the Standard test user, on the Billing page. DevTools open on the Network tab with "Preserve log" OFF. |
| **Test data** | `tpg@example.com` / `password`. Note the "Renew at" date before clicking (expected Oct 30, 2026 for the demo user). |

**Steps**
1. Write down the current "Renew at" date.
2. Click **Upgrade to Premium**.
3. Watch the browser tab: note whether the page flashes, shows "Loading billing...", or the tab's loading spinner runs.
4. Read the plan card price, the three usage cards and the Plan perks card.
5. Read the "Renew at" date again.

**Expected result**
- The page updates instantly. There is no full page reload, no "Loading billing..." state and no browser loading spinner.
- The price reads **$40/month**.
- The usage cards read **Video quality: 4K Ultra HD**, **Watch at the same time: Can watch on 4 devices at once** and **Download on devices: Can download on 6 devices**.
- The Plan perks card lists **Ad-free streaming**, **Spatial audio (select titles)** and **Dolby Vision (select titles)**.
- The "Renew at" date is **identical** to the one written down in step 1.

**Pass/Fail criteria**: PASS only if every value matches exactly (spelling included) and the renewal date is unchanged.
**Cleanup**: reload the page to return to Standard (see TC-E2E-06).

### TC-E2E-05: After upgrading, the page confirms Premium and removes the button

| Field | Value |
|-------|-------|
| **Traces to** | AC-6, AC-2 / REQ-F-06, REQ-F-07, REQ-F-05, REQ-F-02 |
| **Type** | E2E |
| **Priority** | P1 |
| **Preconditions** | Logged in as the Standard test user, on the Billing page, with no upgrade clicked yet |
| **Test data** | `tpg@example.com` / `password` |

**Steps**
1. Confirm that no "You're now on Premium!" message is visible before clicking.
2. Click **Upgrade to Premium**.
3. Look for a success message below the plan row.
4. Look for the Upgrade to Premium button.
5. Read the "Current plan:" badge and the heading above the usage cards.
6. Wait 30 seconds without interacting, then look at the success message again.

**Expected result**
- Before the click there is no success message.
- After the click the text **You're now on Premium!** is shown below the plan row, in green.
- The Upgrade to Premium button is **no longer shown** (now that the plan is Premium).
- The badge reads **Premium** and the heading reads **What's included with Premium**.
- After 30 seconds the success message is **still visible** (it stays until the page is refreshed).

**Pass/Fail criteria**: PASS if every expected result holds.
**Cleanup**: reload the page.

### TC-E2E-06: The upgrade is not saved, so a reload returns to Standard

| Field | Value |
|-------|-------|
| **Traces to** | AC-7 / REQ-F-10 |
| **Type** | E2E |
| **Priority** | P1 |
| **Preconditions** | Logged in as the Standard test user, having just completed TC-E2E-05 (page shows Premium) |
| **Test data** | `tpg@example.com` / `password` |

**Steps**
1. Press F5 (or the browser reload button) on the Billing page.
2. Wait for loading to finish.
3. Read the badge, heading, price and usage cards, and look for the button and the success message.
4. Navigate away (log out, then log back in) and open Billing again.

**Expected result**
- After the reload: badge **Standard**, heading **What's included with Standard**, price **$20/month**, Standard usage values (Full HD (1080p); 2 devices; 2 downloads).
- The **Upgrade to Premium** button is visible again and **You're now on Premium!** is not shown.
- The same Standard state is shown after logging out and back in.

**Pass/Fail criteria**: PASS if the page is fully back to Standard both times.
**Cleanup**: none.

### TC-E2E-07: Standard Billing display is unchanged when no upgrade happens (regression)

| Field | Value |
|-------|-------|
| **Traces to** | AC-9 / REQ-NF-02 |
| **Type** | E2E |
| **Priority** | P1 |
| **Preconditions** | Backend freshly started. Logged in as the Standard test user. No upgrade clicked. |
| **Test data** | `tpg@example.com` / `password` |

**Steps**
1. Open the Billing page and wait for loading to finish.
2. Read the headings: "Plan & Billing" and "Manage your plan and payments".
3. Read the plan card: "Monthly plan", the price, and the **Active** badge.
4. Read the Renew at card.
5. Hover over each usage card and read its tooltip.
6. Read the Plan perks card, including each perk's "% used" value and bar.

**Expected result**
- The title is **Plan & Billing** and the subtitle is **Manage your plan and payments**.
- The plan card shows **Monthly plan**, **$20/month** and an **Active** badge.
- Renew at shows **Oct 30, 2026**.
- The usage cards read **Full HD (1080p)**, **Can watch on 2 devices at once** and **Can download on 2 devices**, and each shows a help tooltip on hover.
- The Plan perks card lists **Ad-free streaming** and **Spatial audio (select titles)**, each **100% used** with a full bar.

**Pass/Fail criteria**: PASS if the display matches exactly. Any missing, reordered or restyled element is a FAIL (regression).
**Cleanup**: none.

### TC-E2E-08: Login, registration and logout still work (regression)

| Field | Value |
|-------|-------|
| **Traces to** | AC-9 / REQ-NF-02 |
| **Type** | E2E |
| **Priority** | P2 |
| **Preconditions** | System Under Test running. Not logged in. |
| **Test data** | Existing user `tpg@example.com` / `password`. New user: name `QA Tester`, email `qa.story11+<timestamp>@example.com`, password `Passw0rd!` |

**Steps**
1. Log in as the existing user and confirm you land on Billing.
2. Click **Logout** and confirm you are returned to the login page.
3. Switch to Sign Up, register the new user, and open Billing.
4. Confirm the new user sees the Standard plan with the **Upgrade to Premium** button.
5. Log out.

**Expected result**
- Login, logout and registration each behave as before the story, with no new errors or blank screens.
- The newly registered user starts on **Standard** and sees the upgrade button.

**Pass/Fail criteria**: PASS if every flow completes normally.
**Cleanup**: restart the backend to discard the registered user (the data is in memory only).
