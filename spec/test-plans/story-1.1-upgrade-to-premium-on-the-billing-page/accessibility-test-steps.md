# Accessibility Test Steps: Story 1.1 Upgrade to Premium on the Billing page (frontend only)

**Purpose**: verify that the new "Upgrade to Premium" button and the success message work for keyboard and screen-reader users.
**Scope**: AC-8 (REQ-NF-03), plus the AC-6 message visibility.
**Derived from**: Story 1.1 AC-8. No application source code was read.

## System Under Test
| Item | Value |
|------|-------|
| Branch | `epic/7344-premium-upgrade-demo-frontend-only` |
| This story's PR | TO CONFIRM: the `[STORY]` PR for Story 1.1, which must be MERGED into the epic branch before execution |
| Confirm the story is in the build | `git log --oneline \| grep -i "1.1"` |
| How to build & run it | **Follow the project's own build docs** (README / CONTRIBUTING / Makefile). This plan does not restate them. |
| Local base URL / port | `http://localhost:5173` |
| Local services that must be up | Backend API on 8000 and frontend dev server on 5173 |
| Test data / accounts to seed | None. Demo user `tpg@example.com` / `password`. |

> If the build or local run fails, that is a **blocker on the dev team**. Report it and do not log functional failures against a system that never started.

Tools: keyboard only (no mouse) for TC-A11Y-01 and 02. A screen reader for TC-A11Y-03: NVDA (Windows), VoiceOver (macOS) or the browser's accessibility inspector.

---

### TC-A11Y-01: The button is reachable by keyboard and shows a visible focus outline (WCAG 2.1.1, 2.4.7)

| Field | Value |
|-------|-------|
| **Traces to** | AC-8 / REQ-NF-03 |
| **Type** | Accessibility |
| **Priority** | P1 |
| **Preconditions** | Logged in as the Standard demo user, on the Billing page, fully loaded. Mouse not used. |
| **Test data** | `tpg@example.com` / `password` |

**Steps**
1. Click into the browser address bar, then press **Tab** repeatedly through the page.
2. Stop when focus reaches the **Upgrade to Premium** button.
3. Observe the button's appearance.

**Expected result**
- The button is reached by Tab in a sensible order: after the top-bar controls (Billing link, Logout), and with no keyboard trap.
- While it is focused, a **clearly visible focus outline or ring** surrounds it, distinguishable from its unfocused state.

**Pass/Fail criteria**: PASS if the button is reachable and its focus indicator is clearly visible.
**Cleanup**: none.

### TC-A11Y-02: The upgrade can be activated with Enter and with Space (WCAG 2.1.1)

| Field | Value |
|-------|-------|
| **Traces to** | AC-8 / REQ-NF-03 |
| **Type** | Accessibility |
| **Priority** | P1 |
| **Preconditions** | As in TC-A11Y-01, with focus on the button |
| **Test data** | `tpg@example.com` / `password` |

**Steps**
1. With focus on **Upgrade to Premium**, press **Enter**.
2. Check that the page now shows $40/month and "You're now on Premium!".
3. Reload the page, Tab to the button again, and press **Space**.
4. Check the page again.
5. After each activation, press Tab once and note where focus goes (the button has been removed).

**Expected result**
- Enter and Space both perform the upgrade exactly as a mouse click does (price $40/month, success message shown, button removed).
- After the button disappears, focus is not lost to an invisible element in a way that traps the user: the next Tab moves to a visible control or wraps normally.

**Pass/Fail criteria**: PASS if both keys upgrade and keyboard navigation continues normally.
**Cleanup**: reload the page.

### TC-A11Y-03: Screen readers announce the success message (WCAG 4.1.3 Status Messages)

| Field | Value |
|-------|-------|
| **Traces to** | AC-8, AC-6 / REQ-NF-03, REQ-F-06 |
| **Type** | Accessibility |
| **Priority** | P1 |
| **Preconditions** | Screen reader running, Billing page loaded as the Standard demo user |
| **Test data** | `tpg@example.com` / `password` |

**Steps**
1. Navigate to the **Upgrade to Premium** button with the screen reader and listen to its announcement.
2. Activate it (Enter).
3. Listen without moving focus.
4. Optionally, in the browser DevTools Accessibility pane, inspect the "You're now on Premium!" element.

**Expected result**
- Step 1: the control is announced as a **button** named **"Upgrade to Premium"**.
- Step 3: the screen reader **automatically announces "You're now on Premium!"** without the user moving to it, as a polite status message.
- Step 4 (optional): the element's role is **status** (live region, polite).

**Pass/Fail criteria**: PASS if the button is announced with its role and name, and the success message is announced automatically.
**Cleanup**: reload the page.

### TC-A11Y-04: Text contrast and 200% zoom (WCAG 1.4.3, 1.4.4)

| Field | Value |
|-------|-------|
| **Traces to** | AC-8, AC-1, AC-6 / REQ-NF-03 |
| **Type** | Accessibility |
| **Priority** | P3 |
| **Preconditions** | Billing page loaded as the Standard demo user |
| **Test data** | A contrast checker (for example the DevTools colour picker contrast ratio) |

**Steps**
1. Check the contrast ratio of the button label against the button background.
2. Upgrade, then check the contrast of the green "You're now on Premium!" text against the page background.
3. Reset, zoom the browser to **200%**, and repeat the upgrade.

**Expected result**
- The button label and the success message text each have a contrast ratio of at least **4.5:1**. TO CONFIRM: if the success-message green falls slightly below 4.5:1, confirm the acceptable colour with the designer, since the requirements do not set a colour.
- At 200% zoom the button and message remain fully visible and usable, with no overlap or clipping, and the upgrade still works.

**Pass/Fail criteria**: PASS if both contrast ratios are at least 4.5:1 and the 200% zoom check passes.
**Cleanup**: reset the zoom to 100%.
