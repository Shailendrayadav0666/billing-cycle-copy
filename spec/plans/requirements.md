# Requirements: Premium Upgrade Demo (Frontend Only)

**Version**: 1
**Epic**: Atlas document 7344, "Epic: Premium Upgrade Demo (Frontend Only)" (`spec/plans/epic-brief.md`)
**Tracker**: LOCAL
**Depth**: Standard
**AIRE Framework**: v1.0
**Generated**: 2026-10-23T11:51:39Z

---

## 1. Intent Analysis

| Aspect | Assessment |
|---|---|
| **User request** | "using aire and helix mcp fetch the solution document and start implementing the epic requirements" |
| **Request type** | Enhancement: adds an interactive upgrade CTA to an existing read-only page |
| **Scope estimate** | Single component: the Billing page (`src/frontend/src/pages/Billing.jsx`) plus its styles (`src/frontend/src/App.css`); dev-only test tooling in `src/frontend/package.json` |
| **Complexity estimate** | Simple: local React state only, no backend or API change |
| **Clarity** | Clear. The Epic and Atlas story doc 7342 fix the behaviour; 7 code-grounded gaps were resolved via `spec/spec-generation/requirement-verification-questions.md` |

---

## 2. Sources and Grounding

### Existing-system truth (Atlas)
- `spec/plans/atlas-deep-dive.md`, Atlas document 6849 "Deep Dive: Billing-Cycle" v29. Relevant points:
  - **Flow 4: View Billing Dashboard.** `Billing.jsx` fetches `GET /api/billing?email=<token>` on mount and keeps the response in `useState` (`data` / `setData`).
  - **Test Coverage Analysis.** 0 tests, 0% coverage, and no test runner is configured in the frontend or the backend.
  - The backend keeps billing data in memory (`billing_data` in `src/backend/main.py`), and every user is seeded on the Standard plan.

### Design references consulted
| # | Reference | Governs | What was extracted |
|---|---|---|---|
| 1 | Atlas document 7342, "Story: Upgrade to Premium Button (Frontend Only)" v7 | The story content for this Epic (per answer Q7 = A) | AC-1 to AC-3; the `PREMIUM_DATA` constant (Premium price, usage cards, perks); `handleUpgrade` merges `PREMIUM_DATA` into state and keeps `renew_at`; button and success-message placement below the plan row and before the section title; CSS classes `upgrade-btn` and `upgrade-success`; Definition of Done |

### Current-code findings that shaped these requirements
- **F1.** `Billing.jsx` hardcodes "Standard" in the current-plan badge (`<span className="standard-badge">Standard</span>`) and in the heading `What's included with Standard`. The Atlas story's code would leave both unchanged after the upgrade. Resolved by Q1 = A (REQ-F-05).
- **F2.** `.btn` in `App.css` is `width: 100%`. Resolved by Q3 = B (REQ-F-08).
- **F3.** The frontend has no test runner. Resolved by Q6 = A (REQ-NF-04).

### Reconciliation: Atlas story doc vs Epic
Story doc 7342's header names the epic "Self-Serve Premium Upgrade". Epic 7344 lists the same story and says "Self-Serve Premium Upgrade" is a separate epic. **Decision (Q7 = A):** story 7342 is this Epic's story content, and its header's epic name is a labelling slip. The Atlas documents themselves are not modified.

Context Project artifacts consulted: none (Existing Knowledge: No, New References: No).

---

## 3. Functional Requirements

| ID | Requirement | Source |
|---|---|---|
| **REQ-F-01** | When the loaded billing data has `plan_name === "Standard"`, the Billing page renders an **"Upgrade to Premium"** button directly below the plan row (plan card + renew card) and before the "What's included" section title. | Epic success metric 1; story 7342 AC-1 |
| **REQ-F-02** | When the billing data has any `plan_name` other than `"Standard"` (including `"Premium"`), the "Upgrade to Premium" button is **not rendered**. | Story 7342 AC-2 |
| **REQ-F-03** | Clicking the button replaces the displayed plan data with hardcoded Premium values via local React state, **without a page reload**. The values are: `plan_name` **Premium**; `price` **$40/month**; usage cards **Video quality: 4K Ultra HD**, **Watch at the same time: Can watch on 4 devices at once** and **Download on devices: Can download on 6 devices** (with the help texts from story 7342); and plan perks **Ad-free streaming**, **Spatial audio (select titles)** and **Dolby Vision (select titles)**, each at `used_percent` 100 with help text "Perks included in your Premium plan." | Epic goal; story 7342 AC-3 and Step 1 |
| **REQ-F-04** | The upgrade preserves the existing `renew_at` value. The "Renew at" date is unchanged after the upgrade. | Story 7342 Step 3 and DoD |
| **REQ-F-05** | Plan labels are data-driven. The current-plan badge text and the section heading ("What's included with &lt;plan&gt;") both render from `data.plan_name`, so they read "Standard" before the upgrade and "Premium" after it. | Q1 = A; finding F1 |
| **REQ-F-06** | After a successful click, the success message **"You're now on Premium!"** is displayed below the button's position. It stays visible until the page is refreshed. | Epic success metric 3; story 7342 AC-3; Q4 = A |
| **REQ-F-07** | After the upgrade the button is no longer rendered, because `plan_name` is now "Premium" (REQ-F-02 applies). | Epic success metric 4; story 7342 AC-3 |
| **REQ-F-08** | The button is auto width (it fits its label) and left-aligned below the plan row. It reuses the existing `.btn` colour and hover styling, and overrides only the full width. | Q3 = B; finding F2 |
| **REQ-F-09** | The Premium badge keeps the existing teal badge styling; only the text changes. | Q2 = A |
| **REQ-F-10** | The upgrade is not persisted. A page refresh re-fetches `/api/billing` and shows the Standard plan again. | Epic out-of-scope (persistence); story 7342 out-of-scope |

---

## 4. Non-Functional Requirements

| ID | Requirement | Source |
|---|---|---|
| **REQ-NF-01** | **No network or backend change.** Clicking the button makes **no** HTTP/API call. `src/backend/**` is not modified, and the `GET /api/billing` contract is unchanged. | Epic goal and out-of-scope; story 7342 AC-3 |
| **REQ-NF-02** | **No regressions.** The existing billing display (loading state, plan card, renew card, usage cards, perks) and the login, registration and logout flows behave exactly as before for every input other than the upgrade click. | Story 7342 DoD |
| **REQ-NF-03** | **Accessibility.** The button is a native `<button>` element: keyboard-operable with Enter and Space, with a visible focus outline. The success message is announced to assistive technology via `role="status"` (implicit `aria-live="polite"`). | Q5 = A |
| **REQ-NF-04** | **Testability.** Vitest, React Testing Library and jsdom are added as **devDependencies only** (no runtime dependency changes), with a `test` script in `src/frontend/package.json`. Billing page unit tests live under `tests/unit/` and must meet the project's `unitTestCoverageMin` threshold for the changed code. | Q6 = A; Atlas Test Coverage Analysis |
| **REQ-NF-05** | **Supply chain (SECURITY-10).** New devDependencies are pinned to exact versions, `package-lock.json` is updated and committed, and the packages come only from the official npm registry. | Security Baseline SECURITY-10 |
| **REQ-NF-06** | **Delivery size.** Delivered in under one day of effort. The production code changes are confined to `Billing.jsx` and `App.css`. | Epic success metric 5 |

---

## 5. Out of Scope

- Any backend endpoint, API call or change to `src/backend/main.py`
- A confirmation modal or proration calculation
- Persisting the upgrade across refreshes or sessions
- A downgrade flow, and any plan tier other than Standard to Premium
- Fixing pre-existing system issues recorded in the Atlas deep dive (for example authentication and secret handling in `main.py`). They are not touched or worsened by this Epic.

---

## 6. Extension Configuration Decisions

| Extension | Decision | Effect |
|---|---|---|
| Security Baseline | Always enforced | Applicable rule: SECURITY-10 (REQ-NF-05). SECURITY-15 is also checked: the click handler cannot throw on valid loaded data, and the button only renders once data is loaded. Other rules are N/A because no new endpoint, data store, network config, authentication or crypto is introduced. |
| UI/UX Mockups | No (skip) | No HTML mockups. The UI is governed by REQ-F-01, F-05, F-06, F-08 and F-09 plus the existing page. |
| Resiliency Baseline | No | Not applied (demo, frontend-only). |
| Property-Based Testing | No | Not applied (UI-only, no algorithmic logic). |

---

## 7. Key Assumptions

- The backend's existing `plan_name` field drives the conditional rendering. It currently returns "Standard" for every user.
- Premium values are exactly those in Atlas story doc 7342 and are hardcoded in the frontend for demo purposes.
- Repeated clicks are not possible, because the button is removed after the first click (REQ-F-07).

---

## 8. Requirements Summary

- **Functional:** 10 (REQ-F-01 to REQ-F-10)
- **Non-functional:** 6 (REQ-NF-01 to REQ-NF-06)
- **Files expected to change:** `src/frontend/src/pages/Billing.jsx` and `src/frontend/src/App.css` (production code); `src/frontend/package.json` and `package-lock.json` (dev tooling); new files under `tests/unit/`
