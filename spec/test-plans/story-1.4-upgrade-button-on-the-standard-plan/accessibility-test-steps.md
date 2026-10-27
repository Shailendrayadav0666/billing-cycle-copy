# Accessibility Test Steps — story-1.4 Upgrade button on the Standard plan

**Purpose**: confirm the "Upgrade to Premium" button is fully usable by keyboard and assistive technology.
**Scope**: AC-3 (REQ-NF-02).

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
| Tester tooling | Keyboard only (no mouse); a screen reader (NVDA or VoiceOver); Chrome DevTools Elements and Accessibility panes |

### TC-A11Y-01 — The button is a native button with an accessible name

| Field | Value |
|-------|-------|
| **Traces to** | AC-3 / REQ-NF-02 — WCAG 2.2 SC 4.1.2 Name, Role, Value |
| **Type** | Accessibility |
| **Priority** | P1 |
| **Preconditions** | Signed in as `tpg@example.com` on the Billing page; screen reader running |
| **Test data** | None |

**Steps**
1. In DevTools Elements, select the "Upgrade to Premium" control and open the Accessibility pane.
2. With the screen reader, move to the control.

**Expected result**
- The element is a `<button>` element (not a `div` or `a` styled as a button).
- The Accessibility pane shows role "button" and name "Upgrade to Premium".
- The screen reader announces "Upgrade to Premium, button".

**Pass/Fail criteria**: PASS if all three hold. Anything else is a FAIL.
**Cleanup**: Stop the screen reader.

### TC-A11Y-02 — The button is reachable by Tab and shows a visible focus outline

| Field | Value |
|-------|-------|
| **Traces to** | AC-3 / REQ-NF-02 — WCAG 2.2 SC 2.1.1 Keyboard, SC 2.4.7 Focus Visible |
| **Type** | Accessibility |
| **Priority** | P1 |
| **Preconditions** | Signed in on the Billing page; mouse not used |
| **Test data** | None |

**Steps**
1. Click into the browser address bar, then press Tab repeatedly until focus reaches "Upgrade to Premium".
2. Look at the button while it has focus.
3. Press Shift+Tab once, then Tab once.

**Expected result**
- Focus reaches the button by Tab alone, in a logical order (after the page header content, before the plan details).
- While focused, the button shows a clearly visible focus outline.
- Shift+Tab moves focus away and Tab returns it.

**Pass/Fail criteria**: PASS if the button is reachable and its focus outline is visible. A button that cannot be focused, or that has no visible focus indicator, is a FAIL.
**Cleanup**: None.

### TC-A11Y-03 — Enter and Space activate the button without errors

| Field | Value |
|-------|-------|
| **Traces to** | AC-3 / REQ-NF-02 — WCAG 2.2 SC 2.1.1 Keyboard |
| **Type** | Accessibility |
| **Priority** | P2 |
| **Preconditions** | As TC-A11Y-02; DevTools Console open and cleared |
| **Test data** | None |

**Steps**
1. Tab to "Upgrade to Premium" and press Enter.
2. Reload the page, Tab to the button again and press Space.
3. Read the Console after each activation.

**Expected result**
- Each key press activates the button: the page accepts the action with no error in the Console. Once Story 1.5 is merged, the page switches to Premium (verified in Story 1.5's plan).
- Neither key press scrolls the page or moves focus unexpectedly.

**Pass/Fail criteria**: PASS if both Enter and Space activate the button with no Console error. Anything else is a FAIL.
**Cleanup**: Reload the page.
