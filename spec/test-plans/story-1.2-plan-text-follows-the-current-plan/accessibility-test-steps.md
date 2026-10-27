# Accessibility Test Steps — story-1.2 Plan text follows the current plan

**Purpose**: confirm the plan badge text stays readable and perceivable for both plans.
**Scope**: AC-1, AC-2 (badge presentation, REQ-NF-03).

## System Under Test
| Item | Value |
|------|-------|
| Branch | `epic/HELIX-7344-premium-upgrade-demo-frontend-only` |
| This story's PR | The `[STORY]` PR for Story 1.2, merged into the epic branch (TO CONFIRM: PR number once raised) |
| Confirm the story is in the build | `git log --oneline \| grep "1.2"` (TO CONFIRM: commit message pattern) |
| How to build & run it | **Follow the project's own build docs** (README / CONTRIBUTING). This plan does not restate them. |
| Local base URL / port | `http://localhost:5173` |
| Local services that must be up | FastAPI backend on port 8000, frontend dev server on port 5173 |
| Test data / accounts to seed | `tpg@example.com` / `password` |
| Tester tooling | A screen reader (NVDA on Windows or VoiceOver on macOS); a contrast checker (for example the Chrome DevTools colour picker contrast ratio); DevTools "Override content" for the Premium case |

### TC-A11Y-01 — Standard badge text is announced and has enough contrast

| Field | Value |
|-------|-------|
| **Traces to** | AC-1 / REQ-F-07, REQ-NF-03 — WCAG 2.2 SC 1.4.3 Contrast (Minimum), SC 1.3.1 Info and Relationships |
| **Type** | Accessibility |
| **Priority** | P2 |
| **Preconditions** | Signed in as `tpg@example.com` on the Billing page; screen reader running |
| **Test data** | None |

**Steps**
1. With the screen reader, read through the page from the "Plan & Billing" heading to the "Current plan" line.
2. Inspect the badge text colour against its background with the contrast checker.

**Expected result**
- The screen reader reads "Current plan: Standard" as text. The badge is not skipped and not read as an image.
- The contrast ratio of the badge text is at least 4.5:1.

**Pass/Fail criteria**: PASS if both hold. Anything else is a FAIL.
**Cleanup**: Stop the screen reader.

### TC-A11Y-02 — Premium badge text is announced and has enough contrast

| Field | Value |
|-------|-------|
| **Traces to** | AC-2 / REQ-F-07, REQ-NF-03 — WCAG 2.2 SC 1.4.3, SC 1.4.1 Use of Color |
| **Type** | Accessibility |
| **Priority** | P2 |
| **Preconditions** | `/api/billing` response overridden with `"plan_name": "Premium"` (see integration-test-steps.md TC-INT-02); screen reader running |
| **Test data** | Override body with `"plan_name": "Premium"` |

**Steps**
1. Reload the Billing page with the override active.
2. With the screen reader, read the "Current plan" line and the section heading.
3. Inspect the Premium badge text colour against its background with the contrast checker.

**Expected result**
- The screen reader reads "Current plan: Premium" and "What's included with Premium". The plan is conveyed by text, not by colour alone.
- The contrast ratio of the Premium badge text is at least 4.5:1.

**Pass/Fail criteria**: PASS if both hold. Anything else is a FAIL.
**Cleanup**: Remove the override, reload, stop the screen reader.
