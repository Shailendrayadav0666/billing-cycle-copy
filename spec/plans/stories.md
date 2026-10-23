EPIC TICKET: Atlas document 7344 — "Epic: Premium Upgrade Demo (Frontend Only)" (LOCAL tracker; Helix solution 951 Billing-Cycle-Helix-Workshop)

# User Stories: Premium Upgrade Demo (Frontend Only)

**Requirements**: `spec/plans/requirements.md` v1
**Personas**: `spec/plans/personas.md`
**Story count**: 1 (user decision, `story-clarification-questions.md` Q1 = A)
**Generated**: 2026-10-23T12:39:07Z
**Built with AIRE v1.0**

> **Sizing-ceiling override (user-approved).** Story 1.1 deliberately exceeds the Step 1.5 ceiling of 5 ACs or fewer and one scenario class per story. It has 10 ACs spanning the visibility rules, the upgrade path and the test baseline. The user chose a single story that mirrors Atlas story doc 7342 and Epic 7344 (answer A on 2026-10-23). The override is recorded in `runtime-artifacts/aire-state.md` (`## Story Planning`) and `runtime-artifacts/audit.md`.

---

## Story 1.1: Upgrade to Premium on the Billing page (frontend only)

**Persona**: Sam, Standard plan subscriber (primary); Priya, demo presenter (secondary); Dev, frontend developer (for AC-10)
**Priority**: High
**Estimate**: XS (under 1 day)
**Source**: Atlas story doc 7342 "Upgrade to Premium Button (Frontend Only)" v7, reconciled per `requirements.md` Section 2
**Covers**: REQ-F-01, REQ-F-02, REQ-F-03, REQ-F-04, REQ-F-05, REQ-F-06, REQ-F-07, REQ-F-08, REQ-F-09, REQ-F-10, REQ-NF-01, REQ-NF-02, REQ-NF-03, REQ-NF-04, REQ-NF-05, REQ-NF-06
**Tracker ID**: LOCAL
**Requires**: none

### Narrative

> **As a** Standard plan subscriber,
> **I want** to click "Upgrade to Premium" on my Billing page and see my plan switch to Premium instantly,
> **so that** stakeholders can experience the upgrade flow before any backend work is built.

### Context

`src/frontend/src/pages/Billing.jsx` is read-only today. It fetches `GET /api/billing` on mount, keeps the response in local state (`data` / `setData`), and hardcodes the word "Standard" in the plan badge and the "What's included" heading. This story makes those labels data-driven. It adds a conditional "Upgrade to Premium" button whose click merges hardcoded Premium data into local state. No backend or API change is involved. It also adds the dev-only test tooling the frontend currently lacks.

### Acceptance Criteria

**AC-1: Button visible on the Standard plan** (REQ-F-01, REQ-F-08)
**Given** a logged-in user whose billing data has `plan_name` "Standard"
**When** the Billing page finishes loading
**Then** an "Upgrade to Premium" button is rendered directly below the plan row (plan card and renew card) and before the "What's included" section title
**And** the button is auto width (it fits its label), left-aligned, and uses the existing `.btn` colour and hover styling

**AC-2: Button hidden on other plans** (REQ-F-02)
**Given** a logged-in user whose billing data has a `plan_name` other than "Standard" (for example "Premium")
**When** the Billing page finishes loading
**Then** the "Upgrade to Premium" button is not rendered

**AC-3: Plan labels follow the plan data** (REQ-F-05, REQ-F-09)
**Given** billing data with a `plan_name` value
**When** the Billing page renders
**Then** the current-plan badge text equals `plan_name`, and keeps the existing teal badge styling
**And** the section heading reads "What's included with" followed by `plan_name`

**AC-4: Click switches the displayed plan to Premium** (REQ-F-03)
**Given** a Standard user on the loaded Billing page
**When** they click "Upgrade to Premium"
**Then**, without a page reload, the page shows:
- Plan: Premium, at $40/month
- Usage cards: Video quality "4K Ultra HD"; Watch at the same time "Can watch on 4 devices at once"; Download on devices "Can download on 6 devices"
- Plan perks: "Ad-free streaming", "Spatial audio (select titles)" and "Dolby Vision (select titles)"

**AC-5: Renewal date is preserved** (REQ-F-04)
**Given** a Standard user whose "Renew at" date is shown
**When** they click "Upgrade to Premium"
**Then** the "Renew at" date is unchanged

**AC-6: Post-upgrade state** (REQ-F-06, REQ-F-07, REQ-F-05)
**Given** the user has just clicked "Upgrade to Premium"
**When** the page re-renders
**Then** the success message "You're now on Premium!" is displayed below the plan row and stays visible
**And** the "Upgrade to Premium" button is no longer rendered
**And** the plan badge reads "Premium" and the heading reads "What's included with Premium"

**AC-7: Local only, so no API call and no persistence** (REQ-NF-01, REQ-F-10)
**Given** the Billing page has loaded its data with the single existing `GET /api/billing` request
**When** the user clicks "Upgrade to Premium"
**Then** no further HTTP request is made
**And** no file under `src/backend/` is changed
**And** when the Billing page is reloaded or remounted, it re-fetches `/api/billing` and shows the Standard plan again

**AC-8: Accessibility** (REQ-NF-03)
**Given** a keyboard or screen-reader user on the Standard plan
**When** they Tab to the "Upgrade to Premium" button and press Enter or Space
**Then** the button shows a visible focus outline and activates the upgrade exactly as a mouse click does
**And** the success message is exposed with `role="status"`, so assistive technology announces it

**AC-9: No regressions to the existing page** (REQ-NF-02, REQ-NF-06)
**Given** the existing Billing behaviour (the "Loading billing..." state, plan card, renew card, usage cards and plan perks for a Standard user) and the login, registration and logout flows
**When** no upgrade click occurs
**Then** everything renders and behaves exactly as before this change
**And** the production code changes are confined to `src/frontend/src/pages/Billing.jsx` and `src/frontend/src/App.css`

**AC-10: Frontend unit-test baseline** (REQ-NF-04, REQ-NF-05)
**Given** the frontend previously had no test runner
**When** this story is delivered
**Then** Vitest, React Testing Library and jsdom are added as **devDependencies only**, pinned to exact versions, with an updated and committed `package-lock.json`, sourced only from the official npm registry
**And** `npm test` in `src/frontend` runs the Billing page unit tests under `tests/unit/`, which exercise AC-1 to AC-9 and meet the `unitTestCoverageMin` threshold for the changed code

### Acceptance Criteria to Requirements

| AC | REQ-IDs |
|---|---|
| AC-1 | REQ-F-01, REQ-F-08 |
| AC-2 | REQ-F-02 |
| AC-3 | REQ-F-05, REQ-F-09 |
| AC-4 | REQ-F-03 |
| AC-5 | REQ-F-04 |
| AC-6 | REQ-F-05, REQ-F-06, REQ-F-07 |
| AC-7 | REQ-NF-01, REQ-F-10 |
| AC-8 | REQ-NF-03 |
| AC-9 | REQ-NF-02, REQ-NF-06 |
| AC-10 | REQ-NF-04, REQ-NF-05 |

### Out of Scope
Backend endpoint or API call; confirmation modal or proration; persistence; downgrade; other plan tiers.

### INVEST Check
- **Independent:** no other story exists.
- **Negotiable:** the ACs were reconciled with the user in Requirements Analysis.
- **Valuable:** a demo-able upgrade experience.
- **Estimable:** XS, under 1 day.
- **Small:** exceeds the ceiling under a **user-approved override**, but is still one PR of about 2 production files plus test tooling.
- **Testable:** every AC is in Given/When/Then form.

---
Built with AIRE v1.0

---

## Requirements Coverage Matrix

| REQ-ID | Covering stories | Status |
|---|---|---|
| REQ-F-01 | 1.1 (AC-1) | Full |
| REQ-F-02 | 1.1 (AC-2) | Full |
| REQ-F-03 | 1.1 (AC-4) | Full |
| REQ-F-04 | 1.1 (AC-5) | Full |
| REQ-F-05 | 1.1 (AC-3, AC-6) | Full |
| REQ-F-06 | 1.1 (AC-6) | Full |
| REQ-F-07 | 1.1 (AC-6) | Full |
| REQ-F-08 | 1.1 (AC-1) | Full |
| REQ-F-09 | 1.1 (AC-3) | Full |
| REQ-F-10 | 1.1 (AC-7) | Full |
| REQ-NF-01 | 1.1 (AC-7) | Full |
| REQ-NF-02 | 1.1 (AC-9) | Full |
| REQ-NF-03 | 1.1 (AC-8) | Full |
| REQ-NF-04 | 1.1 (AC-10) | Full |
| REQ-NF-05 | 1.1 (AC-10) | Full |
| REQ-NF-06 | 1.1 (AC-9) | Full |

**Coverage: 16/16 REQ-IDs fully covered by story ACs.**
