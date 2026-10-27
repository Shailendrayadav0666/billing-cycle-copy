# Accessibility Test Steps — story-1.6 Post-upgrade confirmation

**Purpose**: confirm the success banner reaches screen-reader users without moving focus, and is readable.
**Scope**: AC-2 (REQ-NF-02, REQ-NF-03).

## System Under Test
| Item | Value |
|------|-------|
| Branch | `epic/HELIX-7344-premium-upgrade-demo-frontend-only` |
| This story's PR | The `[STORY]` PR for Story 1.6, merged into the epic branch (TO CONFIRM: PR number once raised) |
| Confirm the story is in the build | `git log --oneline \| grep "1.6"` (TO CONFIRM: commit message pattern) |
| How to build & run it | **Follow the project's own build docs** (README / CONTRIBUTING). This plan does not restate them. |
| Local base URL / port | `http://localhost:5173` |
| Local services that must be up | FastAPI backend on port 8000, frontend dev server on port 5173 |
| Test data / accounts to seed | `tpg@example.com` / `password` |
| Tester tooling | A screen reader (NVDA on Windows or VoiceOver on macOS); Chrome DevTools Elements and Accessibility panes; a contrast checker |

### TC-A11Y-01 — The banner is announced by a screen reader when it appears

| Field | Value |
|-------|-------|
| **Traces to** | AC-2 / REQ-NF-02 — WCAG 2.2 SC 4.1.3 Status Messages |
| **Type** | Accessibility |
| **Priority** | P1 |
| **Preconditions** | Signed in on the Billing page; screen reader running; mouse not used |
| **Test data** | None |

**Steps**
1. Tab to **Upgrade to Premium**.
2. Press Enter.
3. Listen to the screen reader without moving focus.

**Expected result**
- The screen reader announces "You're now on Premium! Enjoy 4K Ultra HD, more screens and more downloads." on its own, without the user navigating to the banner.
- The announcement waits for current speech to finish (polite) and does not interrupt it.

**Pass/Fail criteria**: PASS if the banner text is announced automatically. Silence, or an announcement only after manually navigating to the banner, is a FAIL.
**Cleanup**: Reload the page; stop the screen reader.

### TC-A11Y-02 — Banner has role "status" and readable contrast

| Field | Value |
|-------|-------|
| **Traces to** | AC-2 / REQ-NF-02, REQ-NF-03 — WCAG 2.2 SC 4.1.3, SC 1.4.3 Contrast (Minimum) |
| **Type** | Accessibility |
| **Priority** | P2 |
| **Preconditions** | Signed in on the Billing page; DevTools open |
| **Test data** | None |

**Steps**
1. Click **Upgrade to Premium**.
2. In DevTools Elements, select the banner and open the Accessibility pane.
3. Check the banner text colour against its background with the contrast checker.

**Expected result**
- The Accessibility pane shows the role **status** (implying `aria-live="polite"`), or an explicit `aria-live="polite"`.
- The banner text contrast ratio is at least 4.5:1.

**Pass/Fail criteria**: PASS if the role is "status" (or a polite live region) and contrast is at least 4.5:1. Anything else is a FAIL.
**Cleanup**: Reload the page.
