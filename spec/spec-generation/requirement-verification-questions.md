# Requirements Clarification Questions

**Epic**: HELIX-7344 — Premium Upgrade Demo (Frontend Only) (`spec/plans/epic-brief.md`)
**Existing-system truth**: `spec/plans/atlas-deep-dive.md` (Atlas via Helix MCP)
**AIRE Framework**: v1.0

## What I already know (no question needed)

- The change is frontend only: `src/frontend/src/pages/Billing.jsx` plus styles in `src/frontend/src/App.css`. There are no backend changes and no new API calls.
- `GET /api/billing` already returns `plan_name` ("Standard" for every user today). The Epic uses it to decide whether the button shows.
- The switch to Premium happens instantly, in local React state. Refreshing the page goes back to Standard. There is no modal, no proration and no downgrade.
- Today `Billing.jsx` hardcodes the "Standard" badge and the "What's included with Standard" heading, and does not read `plan_name` at all. The atlas deep dive (Flow 4) confirms this.
- The repo has no test runner and no tests at all (atlas deep dive, Test Coverage Analysis: 0 tests, 0% coverage).

Please fill in every `[Answer]:` tag below with a letter, or with X plus your own text.

---

## Question 1
What should the Premium plan show after the upgrade? This sets the hardcoded values the page switches to.

A) Use this proposed set:
   - Price: `$25/month`
   - Video quality: `4K Ultra HD + HDR`
   - Watch at the same time: `Can watch on 4 devices at once`
   - Download on devices: `Can download on 6 devices`
   - Plan perks: Ad-free streaming, Spatial audio (select titles), Dolby Atmos (select titles)
   - Help/tooltip texts reworded to say "Premium" instead of "Standard"

B) Pull the Atlas story document "Story: Upgrade to Premium Button (Frontend Only)" (Atlas doc 7342) and use the Premium values written there. I'll read it during this stage.

X) Other (please describe after [Answer]: tag below, e.g. your own price and values)

[Answer]: a

## Question 2
What should "Renew at" show after the upgrade?

A) Keep the current renewal date unchanged

B) Show a new date 30 days from today

X) Other (please describe after [Answer]: tag below)

[Answer]: a

## Question 3
Where should the "Upgrade to Premium" button sit on the Billing page?

A) In the page header, right-aligned on the same row as the "Plan & Billing" title

B) Directly next to the "Current plan: Standard" badge

C) Inside the "Monthly plan" card, under the price

X) Other (please describe after [Answer]: tag below)

[Answer]: a

## Question 4
How should the success message behave?

A) An inline success banner at the top of the page that stays until the page is reloaded

B) An inline success banner that disappears on its own after about 5 seconds

C) An inline success banner with a close (x) button that the user dismisses

X) Other (please describe after [Answer]: tag below)

[Answer]: a

## Question 5
What should the success message say?

A) "You're now on Premium! Enjoy 4K Ultra HD, more screens and more downloads."

B) "Upgrade successful. Your plan is now Premium."

X) Other (please write the exact text after [Answer]: tag below)

[Answer]: a

## Question 6
After the upgrade, should the plan name text on the page change too, or only the values?

A) Everything plan-related switches: the "Current plan" badge reads "Premium" (with its own style), the heading reads "What's included with Premium", and price, usage cards and perks all switch

B) Only the values switch (price, usage cards, perks); the badge and heading text stay as they are

X) Other (please describe after [Answer]: tag below)

[Answer]: a

## Question 7
When exactly should the button appear?

A) Only when `plan_name` is exactly "Standard"; hidden for any other value, including Premium

B) Whenever `plan_name` is anything other than "Premium"

X) Other (please describe after [Answer]: tag below)

[Answer]: a

## Question 8
The repo has no frontend test runner. Each story's implementation runs a unit-test gate with a minimum coverage threshold, so a test setup has to be added. Which one?

A) Vitest + React Testing Library + jsdom as dev dependencies, with `test` and `test:coverage` npm scripts (fits the existing Vite setup)

B) Jest + React Testing Library + babel-jest as dev dependencies

X) Other (please describe after [Answer]: tag below)

[Answer]: a

## Question 9
The Billing page currently swallows fetch errors and gets stuck on "Loading billing..." (atlas deep dive, Flow 4). Should this epic fix that?

A) No, keep it out of scope. The Epic is a tightly scoped demo.

B) Yes, add a visible error state when `/api/billing` fails

X) Other (please describe after [Answer]: tag below)

[Answer]: a

## Question 10
What accessibility bar should the new button and success message meet?

A) Native `<button>` with a clear text label, keyboard operable, visible focus outline, and the success message announced to screen readers (`role="status"`, polite live region)

B) No specific accessibility requirements beyond the existing page

X) Other (please describe after [Answer]: tag below)

[Answer]: a

---

## Question: UI/UX Mockups
Once the design stages are complete, should HTML mockups of the user interface be produced for your review before development begins?

A) Yes, produce HTML mockups for review

B) No, designs already exist. Place them in spec/context-project/new-references/ and enter the path after [Answer]:

C) No, skip this step

X) Other (please describe after [Answer]: tag below)

[Answer]: b

## Question: Resiliency Extensions
Should the resiliency baseline be applied to this project?

**What this extension is.** Enabling it applies a set of **directional, design-time best practices** for building resilient systems, derived from the **AWS Well-Architected Framework (Reliability Pillar)** and resilience-review guidance. It steers requirements, design, and code toward fault tolerance, high availability, observability, and recoverability — covering 15 practice areas across business goals, change management, observability, high availability, disaster recovery, and continuous improvement.

**What this extension is NOT.** Enabling it does **not** make your workload production-ready, nor does it certify or guarantee any availability, RTO, or RPO target. It is a **starting point** that scaffolds good resiliency decisions early — it is not a substitute for a formal **AWS Well-Architected Review** of the built system.

Treat the output as a well-grounded **first draft of your resiliency posture** to build on and validate — not a finished, production-certified result.

A) Yes — apply the resiliency baseline as directional best practices and design-time guidance (recommended for business-critical workloads, as an informed starting point that you can validate and harden before go-live)

B) No — skip the resiliency baseline (suitable for PoCs, prototypes, and experimental projects where rapid iteration matters more than reliability)

X) Other (please describe after [Answer]: tag below)

[Answer]: b

## Question: Property-Based Testing Extension
Should property-based testing (PBT) rules be enforced for this project?

A) Yes — enforce all PBT rules as blocking constraints (recommended for projects with business logic, data transformations, serialization, or stateful components)

B) Partial — enforce PBT rules only for pure functions and serialization round-trips (suitable for projects with limited algorithmic complexity)

C) No — skip all PBT rules (suitable for simple CRUD applications, UI-only projects, or thin integration layers with no significant business logic)

X) Other (please describe after [Answer]: tag below)

[Answer]: c

---

## Follow-up Questions

## Follow-up 1 (UI/UX Mockups answer is incomplete)
You answered **B** to the UI/UX Mockups question ("designs already exist"), but no path was given. `spec/context-project/new-references/` is empty, and at the Context question you answered "2) no" (no new references). Which of these do you mean?

A) Designs exist: I have placed them under spec/context-project/new-references/ and I write the exact path after [Answer]: (for example `A spec/context-project/new-references/premium-upgrade/`)

B) No designs exist and no mockups are needed: skip the mockup step (same as option C of the original question)

C) No designs exist, so produce HTML mockups for my review (same as option A of the original question)

X) Other (please describe after [Answer]: tag below)

[Answer]: b
