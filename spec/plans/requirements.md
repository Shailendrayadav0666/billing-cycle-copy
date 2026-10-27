# Requirements: Premium Upgrade Demo (Frontend Only)

**Epic**: HELIX-7344 — Premium Upgrade Demo (Frontend Only)
**Tracker**: LOCAL
**Version**: 1
**AIRE Framework**: v1.0
**Status**: Draft, awaiting approval

---

## 1. Intent Analysis Summary

| Item | Value |
|---|---|
| User request | "using aire and helix mcp, fetch the epic and deep dive documents and start the workflow". What to build comes from the Atlas Epic (`spec/plans/epic-brief.md`). |
| Request type | Enhancement: a new feature on an existing page |
| Scope estimate | Single component: the Billing page (`src/frontend/src/pages/Billing.jsx`) plus styles (`src/frontend/src/App.css`). Test tooling is added to `src/frontend/package.json`. |
| Complexity estimate | Simple |
| Requirements depth | Standard |

**Goal (from the Epic)**: a quick, convincing demo of the Premium upgrade, done entirely in the frontend. A Standard-plan user clicks "Upgrade to Premium" on the Billing page. The whole plan display switches to Premium instantly in local React state, with no backend change and no API call.

---

## 2. Sources Consulted

| Source | What it gave |
|---|---|
| `spec/plans/epic-brief.md` (Atlas Epic doc 7344, via Helix MCP) | Goal, success metrics, scope and out-of-scope list |
| `spec/plans/atlas-deep-dive.md` (Atlas doc 6849, via Helix MCP) | Flow 4 (View Billing Dashboard), the `billing_data` shape, Test Coverage Analysis (0 tests), the error-handling gap |
| `spec/spec-generation/requirement-verification-questions.md` | User answers: Q1–Q10 all A; UI/UX Mockups B, then Follow-up 1 B (skip); Resiliency B (No); PBT C (No) |
| Code read for grounding | `src/frontend/src/pages/Billing.jsx`, `src/backend/main.py`, `src/frontend/package.json` |

- **Context Project artifacts consulted**: none. Both Existing Knowledge and New References were answered "no".
- **New References consulted**: none.
- **Design references consulted**: none were named.

### Existing-system observations (Atlas and code agree; no Atlas conflict)

- `GET /api/billing?email=` returns `{plan_name, price, renew_at, usages[], included_usage{}}`. `plan_name` is "Standard" for every user today.
- `Billing.jsx` hardcodes the "Standard" badge and the "What's included with Standard" heading. It does not read `plan_name`.
- `Billing.jsx` fetches without a `.catch()`. If the call fails, the page stays on "Loading billing..." forever (deep dive, Flow 4).
- There is no test runner and there are no tests in the repo (deep dive, Test Coverage Analysis).

---

## 3. Functional Requirements

| ID | Requirement | Source |
|---|---|---|
| REQ-F-01 | The Billing page shows an **"Upgrade to Premium"** button, right-aligned in the page header on the same row as the "Plan & Billing" title. | Epic success metric 1; Q3 |
| REQ-F-02 | The button shows **only** when the current plan is exactly `"Standard"`. The current plan starts from `plan_name` in the `/api/billing` response. For any other value, including `"Premium"`, the button is hidden. | Epic; Q7 |
| REQ-F-03 | Clicking the button switches the page's current plan to Premium **instantly**, in local component state. There is no API call, no page reload, no confirmation modal and no artificial delay. | Epic goal and scope |
| REQ-F-04 | After the upgrade, the plan card price shows **`$25/month`**. | Q1 |
| REQ-F-05 | After the upgrade, the three usage cards show the Premium values, keeping their existing ids, icons and order:<br>- **Video quality**: `4K Ultra HD + HDR`. Tooltip: "The best video resolution available on the Premium plan."<br>- **Watch at the same time**: `Can watch on 4 devices at once`. Tooltip unchanged; it does not name a plan.<br>- **Download on devices**: `Can download on 6 devices`. Tooltip unchanged; it does not name a plan. | Q1 |
| REQ-F-06 | After the upgrade, the "Plan perks" card lists **Ad-free streaming**, **Spatial audio (select titles)** and **Dolby Atmos (select titles)**, each at 100%. Its help text reads "Perks included in your Premium plan." | Q1 |
| REQ-F-07 | Plan-name text follows the current plan instead of being hardcoded. The "Current plan" badge shows the plan name ("Standard" before the upgrade, **"Premium"** after it, with a distinct Premium badge style), and the section heading reads "What's included with {plan}". | Q6 |
| REQ-F-08 | "Renew at" keeps the date from the `/api/billing` response; the upgrade does not change it. | Q2 |
| REQ-F-09 | After the upgrade, a success banner appears at the top of the Billing page with the exact text: **"You're now on Premium! Enjoy 4K Ultra HD, more screens and more downloads."** It stays visible until the page is reloaded. It has no close button and no timeout. | Epic success metric 3; Q4; Q5 |
| REQ-F-10 | After the upgrade, the "Upgrade to Premium" button is no longer shown. | Epic success metric 4 |
| REQ-F-11 | Nothing is persisted. Reloading or revisiting the page re-fetches `/api/billing`, which shows Standard again with the button and without the banner. | Epic out of scope |
| REQ-F-12 | Everything else on the page stays as it is: "Monthly plan" label, "Active" badge, page subtitle, section sub-copy and the loading state. | Epic scope (no other changes) |

---

## 4. Non-Functional Requirements

| ID | Requirement | Source |
|---|---|---|
| REQ-NF-01 | **Frontend only.** No change under `src/backend/`. The Billing page still makes exactly one network call, the existing `GET /api/billing`. | Epic out of scope |
| REQ-NF-02 | **Accessibility.**<br>- The button is a native `<button>` with the visible text label "Upgrade to Premium".<br>- It works by keyboard (Tab to focus, Enter or Space to activate) and has a visible focus outline.<br>- The success banner is announced to screen readers (`role="status"`, polite live region). | Q10 |
| REQ-NF-03 | **Styling.** New styles (button, success banner, Premium badge) live in `src/frontend/src/App.css`. They follow the page's existing class naming and visual language, and the layout keeps working at the widths the page already supports. | Epic in scope |
| REQ-NF-04 | **Maintainability.** The Premium values (price, usages, perks, help texts) sit in a single constant with the same shape as the `/api/billing` response, so one rendering path draws both Standard and Premium. | Q1 values; existing response shape |
| REQ-NF-05 | **Unit test tooling.**<br>- Add Vitest, React Testing Library and jsdom to `src/frontend/package.json` as **dev dependencies**, with `test` and `test:coverage` npm scripts.<br>- The new behaviour (REQ-F-01 to REQ-F-12) is covered by unit tests that meet the project's `unitTestCoverageMin` threshold.<br>- `/api/billing` is mocked in tests, never called for real. | Q8; AIRE unit-test gate |
| REQ-NF-06 | **Supply chain (SECURITY-10).**<br>- The new dev dependencies are installed from the official npm registry and pinned in the committed `src/frontend/package-lock.json`.<br>- `npm audit` is run after install, and the result is recorded with the story's evidence.<br>- No runtime (non-dev) dependency is added. | Security Baseline |
| REQ-NF-07 | **Output safety.** All Premium text is rendered as JSX text (escaped by React). No `dangerouslySetInnerHTML` and no raw HTML injection. | Security Baseline (XSS hygiene) |
| REQ-NF-08 | **Fail-safe fetch (SECURITY-15).** The existing `/api/billing` fetch, in the component this epic edits, gets an explicit `.catch()` so it can no longer raise an unhandled promise rejection. In line with Q9, **no visible error UI is added**: on failure the page keeps its current loading state and shows no internal error details. | Security Baseline (always enforced); Q9 |
| REQ-NF-09 | **Misuse consideration (SECURITY-11).** The upgrade is cosmetic. It grants no entitlement and changes no billing or server-side data, so tampering with client-side state cannot affect any user's real plan. | Security Baseline |

---

## 5. Out of Scope

- Any backend endpoint, API call or data change. A real upgrade is covered by the separate "Self-Serve Premium Upgrade" Epic.
- Confirmation modal, proration calculation, payment.
- Persisting the upgrade across reloads or sessions.
- Downgrade flow and any other plan tier.
- A visible error state for a failed `/api/billing` call (Q9). Only the fail-safe `.catch()` in REQ-NF-08 is in scope.
- Pre-existing security debt recorded in the deep dive, which this epic does not touch:
  - the email used as the bearer token
  - plaintext passwords in the mock store
  - CORS `allow_origins=["*"]`
  - missing HTTP security headers
  - missing structured logging

---

## 6. Assumptions and Constraints

- `plan_name` values are case-sensitive; only the exact string `"Standard"` shows the button (REQ-F-02).
- The demo is shown with the existing mock user (`tpg@example.com`) or a newly registered user. Both are Standard.
- The Premium tooltip for "Video quality" and the perks help text are reworded. Tooltips that don't name a plan are left unchanged.

---

## 7. Extension Configuration

| Extension | Enabled | Notes |
|---|---|---|
| Security Baseline | Yes (always enforced) | See Section 8 |
| UI/UX Mockups | No | First answer B, then Follow-up 1 B: skip the mockup step |
| Resiliency Baseline | No | Answered B |
| Property-Based Testing | No | Answered C |

---

## 8. Security Baseline Compliance (Requirements stage)

| Rule | Status | Rationale |
|---|---|---|
| SECURITY-01 Encryption at rest/in transit | N/A | No data store is added or changed |
| SECURITY-02 Access logging on intermediaries | N/A | No load balancer, gateway or CDN is involved |
| SECURITY-03 Application-level logging | N/A | No new deployable component; the missing logging is pre-existing debt (Section 5) |
| SECURITY-04 HTTP security headers | N/A | No HTML-serving endpoint changes; the missing headers are pre-existing debt (Section 5) |
| SECURITY-05 Input validation on API parameters | N/A | No API endpoint is added or changed (REQ-NF-01) |
| SECURITY-06 Least-privilege access policies | N/A | No IAM or policy resources |
| SECURITY-07 Restrictive network configuration | N/A | No network resources |
| SECURITY-08 Application-level access control | N/A | No new protected resource; the Billing route stays behind the existing ProtectedRoute |
| SECURITY-09 Hardening and misconfiguration | N/A | No configuration or deployment changes |
| SECURITY-10 Software supply chain | Compliant | REQ-NF-06: official registry, pinned lock file, `npm audit`, dev-only additions |
| SECURITY-11 Secure design principles | Compliant | REQ-NF-09 records the misuse case; no security-critical logic is added |
| SECURITY-12 Authentication and credentials | N/A | Authentication is unchanged; no credentials are added |
| SECURITY-13 Software and data integrity | N/A | No artifacts, deserialization or update channels are involved |
| SECURITY-14 Alerting and monitoring | N/A | No deployable infrastructure |
| SECURITY-15 Exception handling and fail-safe defaults | Compliant | REQ-NF-08: an explicit `.catch()` on the fetch in the edited component; no internal details shown |
| SECURITY-16 Cryptographic standards | N/A | No cryptography is involved |

No blocking security findings.

---

## 9. Key Requirements Summary

- One new header button, shown only on the Standard plan, that switches the Billing page to Premium in local state ($25/month, 4K Ultra HD + HDR, 4 screens, 6 download devices, three perks).
- The plan badge and heading follow the current plan. A persistent, screen-reader-announced success banner appears, and the button disappears after the upgrade.
- No backend change and no persistence: a reload goes back to Standard.
- Adds Vitest and React Testing Library unit test tooling as pinned dev dependencies, plus a fail-safe `.catch()` on the existing fetch.
