EPIC TICKET: HELIX-7344 — Epic: Premium Upgrade Demo (Frontend Only) (Atlas Epic document 7344; tracker LOCAL, no external URL)

# User Stories: Premium Upgrade Demo (Frontend Only)

**Requirements**: `spec/plans/requirements.md` v1
**Personas**: `spec/plans/personas.md`
**Breakdown**: feature-based with SPIDR slicing, 6 stories, team_size 2
**Acceptance criteria format**: Given / When / Then (each AC becomes one `@AC-n` scenario in the story's `.feature` contract)
**AIRE Framework**: v1.0

Every story is built in `src/frontend/` only. Each story's unit tests mock `/api/billing`; no test calls the real backend.

---

## Story 1.1: Frontend unit-test tooling

**Tracker ID**: LOCAL
**Requires**: none
**Persona**: P2 Product stakeholder
**Covers**: REQ-NF-05, REQ-NF-06
**SPIDR**: scaffolding (the unit-test gate of every other story needs it)

As a **product stakeholder**, I want the Billing page's behaviour checked by automated unit tests so that the demo works the same way every time it is shown.

### Acceptance Criteria

- **AC-1** (REQ-NF-05, REQ-NF-06)
  Given the frontend has no test runner,
  When this story is complete,
  Then `src/frontend/package.json` lists Vitest, React Testing Library and jsdom as **devDependencies** only, and no runtime dependency is added.
- **AC-2** (REQ-NF-05)
  Given the frontend folder,
  When a developer runs `npm run test`,
  Then Vitest runs in a jsdom environment and passes a smoke test that renders the Billing page against a mocked `/api/billing` response.
- **AC-3** (REQ-NF-05)
  Given the frontend folder,
  When a developer runs `npm run test:coverage`,
  Then a coverage report (text summary and lcov) is produced that the unit-test gate can check against `unitTestCoverageMin`.
- **AC-4** (REQ-NF-06)
  Given the new dev dependencies are installed from the official npm registry,
  When the story is committed,
  Then their exact resolved versions are pinned in the committed `src/frontend/package-lock.json`, and the `npm audit` result is recorded in the story's evidence.

---

## Story 1.2: Plan text follows the current plan

**Tracker ID**: LOCAL
**Requires**: 1.1
**Persona**: P1 Standard-plan subscriber
**Covers**: REQ-F-07, REQ-F-12, REQ-NF-03
**SPIDR**: Rules (a rendering rule, separate from the upgrade action)

As a **Standard-plan subscriber**, I want the plan name on the Billing page to come from my actual plan so that the page always tells me correctly which plan I'm on.

### Acceptance Criteria

- **AC-1** (REQ-F-07)
  Given `/api/billing` returns `plan_name` "Standard",
  When the Billing page loads,
  Then the "Current plan" badge reads "Standard" and the section heading reads "What's included with Standard".
- **AC-2** (REQ-F-07, REQ-NF-03)
  Given the current plan is "Premium",
  When the Billing page renders,
  Then the badge reads "Premium" in a distinct Premium badge style, and the heading reads "What's included with Premium".
- **AC-3** (REQ-F-12)
  Given any current plan,
  When the Billing page renders,
  Then the "Monthly plan" label, "Active" badge, page subtitle and section sub-copy render exactly as they do today.
- **AC-4** (REQ-F-12)
  Given the `/api/billing` response has not arrived yet,
  When the Billing page renders,
  Then "Loading billing..." is shown exactly as today.

**Constraint**: the Premium badge style lives in `src/frontend/src/App.css` and follows the existing class naming (REQ-NF-03).

---

## Story 1.3: Fail-safe billing fetch

**Tracker ID**: LOCAL
**Requires**: 1.1
**Persona**: P1 Standard-plan subscriber (secondary: P2 Product stakeholder)
**Covers**: REQ-NF-08
**SPIDR**: Paths (the failure path of the existing fetch)

As a **Standard-plan subscriber**, I want the Billing page to handle a failed billing request safely so that the page never crashes or exposes error details when the service is unavailable.

### Acceptance Criteria

- **AC-1** (REQ-NF-08)
  Given the `/api/billing` request rejects (for example a network error),
  When the Billing page loads,
  Then the rejection is caught (no unhandled promise rejection) and the page keeps showing "Loading billing...".
- **AC-2** (REQ-NF-08)
  Given `/api/billing` responds with a non-OK status (for example 401 "Not authenticated"),
  When the Billing page loads,
  Then the response body is not used as billing data, the page does not crash, and it keeps showing "Loading billing...".
- **AC-3** (REQ-NF-08)
  Given either failure above,
  When the page is shown,
  Then no internal detail (status code, response body, stack trace) is displayed to the user.

**Note**: AC-2 closes a real gap. Today a 401 body is passed to `setData`, and rendering then fails on `data.usages.map`. The Atlas deep dive (Flow 4) describes this case as "data stays null"; the code shows otherwise.

---

## Story 1.4: Upgrade button on the Standard plan

**Tracker ID**: LOCAL
**Requires**: 1.1
**Persona**: P1 Standard-plan subscriber
**Covers**: REQ-F-01, REQ-F-02, REQ-NF-02, REQ-NF-03
**SPIDR**: Rules (the visibility rule for the call to action)

As a **Standard-plan subscriber**, I want to see an "Upgrade to Premium" button on the Billing page so that I know I can move to a better plan.

### Acceptance Criteria

- **AC-1** (REQ-F-01, REQ-NF-03)
  Given the current plan is exactly "Standard",
  When the Billing page renders,
  Then an "Upgrade to Premium" button is shown, right-aligned in the page header on the same row as the "Plan & Billing" title.
- **AC-2** (REQ-F-02)
  Given the current plan is anything other than exactly "Standard" (for example "Premium" or "standard"),
  When the Billing page renders,
  Then no "Upgrade to Premium" button is rendered.
- **AC-3** (REQ-NF-02)
  Given the button is shown,
  When a keyboard user tabs to it and presses Enter or Space,
  Then it is a native `<button>` with the visible text "Upgrade to Premium", shows a visible focus outline, and invokes the upgrade action.

**Constraint**: the button style lives in `src/frontend/src/App.css` and follows the existing class naming (REQ-NF-03). What the upgrade action does is defined in Story 1.5.

---

## Story 1.5: Switch the plan display to Premium on click

**Tracker ID**: LOCAL
**Requires**: 1.2, 1.4
**Persona**: P1 Standard-plan subscriber (secondary: P2 Product stakeholder)
**Covers**: REQ-F-03, REQ-F-04, REQ-F-05, REQ-F-06, REQ-F-08, REQ-NF-01, REQ-NF-04, REQ-NF-07, REQ-NF-09
**SPIDR**: Data (the Premium data variant)

As a **Standard-plan subscriber**, I want clicking "Upgrade to Premium" to show me the Premium plan straight away so that I can see what I get without waiting.

### Acceptance Criteria

- **AC-1** (REQ-F-03, REQ-NF-01, REQ-NF-09)
  Given a Standard user on the Billing page,
  When they click "Upgrade to Premium",
  Then the page switches to Premium in the same render: the badge reads "Premium" and the heading reads "What's included with Premium" (the Story 1.2 rule). This happens with no additional network request, no page reload, no confirmation dialog and no storage write.
- **AC-2** (REQ-F-04)
  Given the user has clicked "Upgrade to Premium",
  When the plan card renders,
  Then the price shows "$25/month".
- **AC-3** (REQ-F-05)
  Given the user has clicked "Upgrade to Premium",
  When the usage cards render,
  Then they keep their ids, icons and order and show:
  - Video quality: "4K Ultra HD + HDR", with the tooltip "The best video resolution available on the Premium plan."
  - Watch at the same time: "Can watch on 4 devices at once"
  - Download on devices: "Can download on 6 devices"

  The tooltips on the last two cards are unchanged.
- **AC-4** (REQ-F-06)
  Given the user has clicked "Upgrade to Premium",
  When the "Plan perks" card renders,
  Then it lists Ad-free streaming, Spatial audio (select titles) and Dolby Atmos (select titles), each at 100%, with the help text "Perks included in your Premium plan."
- **AC-5** (REQ-F-08)
  Given the user has clicked "Upgrade to Premium",
  When the plan row renders,
  Then "Renew at" still shows the date from the `/api/billing` response.

**Constraints** (checked at code review):
- C-1 (REQ-NF-01): no file under `src/backend/` changes.
- C-2 (REQ-NF-04): the Premium values live in one constant with the same shape as the `/api/billing` response, drawn by the same rendering path as Standard.
- C-3 (REQ-NF-07): all Premium text is rendered as JSX text; no `dangerouslySetInnerHTML`.
- C-4 (REQ-NF-09): the upgrade changes component state only. It grants no entitlement and changes no server-side data.

---

## Story 1.6: Post-upgrade confirmation

**Tracker ID**: LOCAL
**Requires**: 1.5
**Persona**: P1 Standard-plan subscriber (secondary: P2 Product stakeholder)
**Covers**: REQ-F-09, REQ-F-10, REQ-F-11, REQ-NF-02, REQ-NF-03, REQ-NF-07
**SPIDR**: Paths (the state after the upgrade)

As a **Standard-plan subscriber**, I want clear confirmation after upgrading so that I know the upgrade worked.

### Acceptance Criteria

- **AC-1** (REQ-F-09, REQ-NF-03)
  Given the user has just clicked "Upgrade to Premium",
  When the page re-renders,
  Then a success banner at the top of the Billing page shows exactly: "You're now on Premium! Enjoy 4K Ultra HD, more screens and more downloads."
- **AC-2** (REQ-NF-02)
  Given the success banner appears,
  When a screen reader is running,
  Then the banner is announced, because it is a polite live region (`role="status"`).
- **AC-3** (REQ-F-09)
  Given the success banner is shown,
  When time passes or the user keeps using the page,
  Then the banner stays visible: it has no close button and no timeout.
- **AC-4** (REQ-F-10)
  Given the user has upgraded,
  When the page re-renders,
  Then the "Upgrade to Premium" button is no longer rendered.
- **AC-5** (REQ-F-11)
  Given the user has upgraded,
  When the Billing page is reloaded or revisited,
  Then `/api/billing` is fetched again, the Standard plan is shown with the "Upgrade to Premium" button, and no success banner is shown.

**Constraints**: the banner style lives in `src/frontend/src/App.css` (REQ-NF-03), and its text is rendered as JSX text (REQ-NF-07).

**Granularity note**: AC-5 (reload) is a second path. It stays in this story because it has no logic of its own: it follows from the upgrade living only in component state.

---

## Requirements Coverage Matrix

| REQ-ID | Covering stories (ACs / constraints) | Status |
|---|---|---|
| REQ-F-01 | 1.4 (AC-1) | Full |
| REQ-F-02 | 1.4 (AC-2) | Full |
| REQ-F-03 | 1.5 (AC-1) | Full |
| REQ-F-04 | 1.5 (AC-2) | Full |
| REQ-F-05 | 1.5 (AC-3) | Full |
| REQ-F-06 | 1.5 (AC-4) | Full |
| REQ-F-07 | 1.2 (AC-1, AC-2); seam to the upgrade owned by 1.5 (AC-1) | Full |
| REQ-F-08 | 1.5 (AC-5) | Full |
| REQ-F-09 | 1.6 (AC-1, AC-3) | Full |
| REQ-F-10 | 1.6 (AC-4) | Full |
| REQ-F-11 | 1.6 (AC-5) | Full |
| REQ-F-12 | 1.2 (AC-3, AC-4) | Full |
| REQ-NF-01 | 1.5 (AC-1, C-1) | Full |
| REQ-NF-02 | 1.4 (AC-3), 1.6 (AC-2) | Full |
| REQ-NF-03 | 1.2 (AC-2, constraint), 1.4 (AC-1, constraint), 1.6 (AC-1, constraint) | Full |
| REQ-NF-04 | 1.5 (C-2) | Full |
| REQ-NF-05 | 1.1 (AC-1, AC-2, AC-3); each later story adds its own unit tests | Full |
| REQ-NF-06 | 1.1 (AC-1, AC-4) | Full |
| REQ-NF-07 | 1.5 (C-3), 1.6 (constraint) | Full |
| REQ-NF-08 | 1.3 (AC-1, AC-2, AC-3) | Full |
| REQ-NF-09 | 1.5 (AC-1, C-4) | Full |

Requirements coverage: 21/21 REQ-IDs fully covered by story ACs and constraints.

## Story Granularity Check

| Story | ACs | New layers | Title conjunction | Scenario classes | Result |
|---|---|---|---|---|---|
| 1.1 | 4 | test tooling only | none | setup | Pass |
| 1.2 | 4 | frontend view | none | rendering rule | Pass |
| 1.3 | 3 | frontend view | none | failure path | Pass |
| 1.4 | 3 | frontend view | none | visibility rule | Pass |
| 1.5 | 5 | frontend view | none | upgrade happy path | Pass |
| 1.6 | 5 | frontend view | none | post-upgrade path (reload AC has no logic of its own; see the note on 1.6) | Pass |

Story granularity: 6 stories, 0 ceiling violations, 0 auto-splits.
