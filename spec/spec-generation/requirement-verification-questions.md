# Requirements Clarification Questions

**Epic**: Premium Upgrade Demo (Frontend Only), from Atlas document 7344
**Inputs read**: `spec/plans/epic-brief.md`, `spec/plans/atlas-deep-dive.md`, Atlas story doc 7342 and the current code in `src/frontend/src/pages/Billing.jsx`, `src/frontend/src/App.css` and `src/backend/main.py`.

The Epic and the Atlas story doc are clear on the main behaviour: the button, the hardcoded Premium values ($40/month, 4K Ultra HD, 4 devices, 6 downloads, the Ad-free / Spatial audio / Dolby Vision perks), local state only, no API call, and reverting on refresh. Those are taken as given.

The questions below cover gaps found by reading the current code. Fill in each `[Answer]:` tag, then tell me in chat when you're done.

---

## Question 1
`Billing.jsx` hardcodes the word "Standard" in two places that the Atlas story's code change does not touch:
- the current-plan badge: `Current plan: <span className="standard-badge">Standard</span>`
- the section heading: `What's included with Standard`

If these are left as they are, the page would still say "Standard" after the upgrade. That would contradict AC-3 ("Plan name: **Premium**") and the Epic goal ("the entire UI switches to Premium"). How should these labels behave?

A) Drive both the badge and the heading from `data.plan_name`, so they read "Premium" after the upgrade (Recommended)

B) Drive only the badge from `data.plan_name` and keep the heading as-is

C) Leave both hardcoded exactly as the Atlas story code shows

X) Other (please describe after [Answer]: tag below)

[Answer]: a

## Question 2
After the upgrade, how should the Premium plan badge look?

A) Same teal styling as today's Standard badge, only the text changes (Recommended for a minimal demo)

B) A distinct Premium style, for example a gold or purple accent, so the change is visually obvious in the demo

X) Other (please describe after [Answer]: tag below)

[Answer]: a

## Question 3
The existing `.btn` class is `width: 100%`, so the Atlas story's `className="btn upgrade-btn"` would make the button stretch across the full width of the billing card. How wide should the "Upgrade to Premium" button be?

A) Full width of the billing card, keeping the `.btn` default

B) Auto width (fits its label), left-aligned below the plan row (Recommended)

X) Other (please describe after [Answer]: tag below)

[Answer]: b

## Question 4
How long should the success message "You're now on Premium!" stay visible?

A) Stays visible until the page is refreshed (Recommended; matches the Atlas story)

B) Disappears automatically after a few seconds (please state how many)

C) Stays until the user dismisses it with a close control

X) Other (please describe after [Answer]: tag below)

[Answer]: a

## Question 5
What accessibility behaviour is expected for the new elements?

A) Announce the success message to screen readers (`role="status"` / `aria-live="polite"`), and make the button keyboard-operable with a visible focus outline (Recommended)

B) Keyboard-operable button only, with no screen-reader announcement

X) Other (please describe after [Answer]: tag below)

[Answer]: a

## Question 6
The frontend has no test framework. The Atlas deep dive reports 0 tests and 0% coverage, and `package.json` has no test script. AIRE's code-generation gates run unit tests to a coverage threshold, so a runner is needed. That means adding dev-only dependencies, which goes slightly beyond the Epic's "one file change" scope. How should unit tests be handled?

A) Add Vitest, React Testing Library and jsdom as **devDependencies** with a `test` script, and put the Billing page tests under `tests/unit/` (Recommended; no runtime dependency changes)

B) No automated unit tests for this demo; rely on the manual test plan only (the unit-test gate would then be recorded as N/A)

X) Other (please describe after [Answer]: tag below)

[Answer]: a

## Question 7
Atlas story doc 7342 says in its header that it belongs to the **"Self-Serve Premium Upgrade"** epic. Epic 7344 lists the same story title, but says "Self-Serve Premium Upgrade" is a separate, full-flow epic. How should story 7342 be treated?

A) Treat story 7342's acceptance criteria and code guidance as the story content for **this** Epic 7344; its header's epic name is a labelling slip (Recommended)

B) Use Epic 7344 only, and derive stories fresh without relying on story 7342

X) Other (please describe after [Answer]: tag below)

[Answer]: a

---

## Question: UI/UX Mockups
Once the design stages are complete, should HTML mockups of the user interface be produced for your review before development begins?

A) Yes, produce HTML mockups for review

B) No, designs already exist. Place them in spec/context-project/new-references/ and enter the path after [Answer]:

C) No, skip this step

X) Other (please describe after [Answer]: tag below)

[Answer]: c

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
