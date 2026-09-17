EPIC TICKET: Self-Serve Premium Upgrade (Atlas via Helix MCP, solution document_id 4039) — Local tracker, no external URL

# User Stories — Self-Serve Premium Upgrade

> **Recorded exception — deliberate user override of Step 18.6 (Story Granularity & Splitting
> Check)**: the user asked for a single story four times (initial answer, after the Step 10
> trade-off flag, after GATE 1's "Request Changes", and after a structured re-confirmation offering
> two compliant alternatives), each time after the sizing-ceiling conflict was explained in full.
> This is recorded as an explicit, informed decision to accept a single, larger story rather than a
> framework compliance failure. **The resulting story deliberately exceeds AIRE's own Step 1.5 hard
> sizing ceilings**: it carries 12 acceptance criteria (ceiling: 5), newly touches two architectural
> layers with real independent logic in each (ceiling: one), and bundles multiple scenario classes —
> commit happy path, dry-run preview, and UI loading/success/error states (ceiling: one). Consequence
> to expect downstream: `dev-implement`'s own code-generation plan and code review for this story will
> be larger and harder to verify as one bounded diff than the 5-story split would have been — this
> trade-off was stated to the user before they confirmed. See `runtime-artifacts/audit.md` for the
> full decision trail (5-story compliant draft, three refusals with reasoning, final override).

---

## Story 1.1: Self-Serve Premium Upgrade

**Persona**: Standard Plan Subscriber

**As a** Standard plan subscriber on the Billing page,
**I want to** upgrade to the Premium plan with a single click, previewing and then confirming a prorated charge,
**so that** I can unlock higher usage limits and on-demand credits without waiting for my next billing cycle.

**Covers**: REQ-F-01, REQ-F-02, REQ-F-03, REQ-F-04, REQ-F-05, REQ-F-06, REQ-F-07, REQ-F-08, REQ-NF-01, REQ-NF-02, REQ-NF-03, REQ-NF-04, REQ-NF-05

**Acceptance Criteria**:
- **AC-1**: Given `plan_name` is `"Standard"`, when the Billing page renders, then the "Upgrade to Premium" button is visible inside the existing `plan-row` section, adjacent to `plan-card`.
- **AC-2**: Given `plan_name` is `"Premium"`, when the Billing page renders, then that area shows a `Premium` badge (reusing the existing `standard-badge` CSS pattern) and the button is not rendered.
- **AC-3**: The upgrade button is keyboard-operable (focusable, activates on Enter/Space) and carries a descriptive `aria-label` (e.g. "Upgrade to Premium plan").
- **AC-4**: Given the user clicks the upgrade button, when the confirmation panel opens, then it calls `POST /api/billing/upgrade?dry_run=true` and displays the Premium price ($50/month), the prorated charge for remaining days, and the unchanged renewal date — with **no** writes to `users` or `billing_data`.
- **AC-5**: The panel shows **Confirm Upgrade** and **Cancel** actions; clicking Cancel dismisses the panel with zero state changes (no commit call made); the upgrade is never committed before the user explicitly clicks **Confirm Upgrade**.
- **AC-6**: Given an unknown `email`, when either the `dry_run` or commit call is made, then the response is `401`.
- **AC-7**: Given a user already on Premium, when either the `dry_run` or commit call is made, then the response is `400 {"detail": "Already on Premium plan"}` and no state changes occur (idempotency).
- **AC-8**: Given a valid Standard-plan email, when the user clicks **Confirm Upgrade**, then `POST /api/billing/upgrade` is called: `users[email].plan` becomes `"Premium"`, `price` becomes `"$50/month"`, `billing_data[email]` usage limits update to the Premium table (chat credits 2,000->10,000; chatbots 3->10; document pages 1,000->5,000) with used amounts AND the on-demand balance carried over unchanged, and `on_demand_usage.notice` updates to `"On-demand credit is available on your Premium plan."`. The response body is `{success: true, prorated_charge, new_plan: "Premium", effective_from, renew_at}`, where `prorated_charge = round((50 - 20) / 30 * days_remaining, 2)`.
- **AC-9**: While the commit call (AC-8) is in flight, a loading spinner is shown on the Confirm button.
- **AC-10**: Given the commit call succeeds, when the response returns, then the app re-fetches `GET /api/billing`, dismisses the confirmation panel, and the plan badge updates to `Premium`.
- **AC-11**: Given the commit call fails, when the response returns an error, then an inline error message is shown below the confirmation panel and the panel stays open so the user can retry.
- **AC-12**: After a successful upgrade, all existing billing page data — usage bars, renewal date, on-demand card — continues to render correctly with the updated Premium values (zero regression). The endpoint responds in under 200ms under normal in-memory operation.

**Requires**: none (single story — nothing else to depend on)

---

## Requirements Coverage Matrix

| REQ-ID | Covering Stories | Status |
|---|---|---|
| REQ-F-01 | 1.1 | Full |
| REQ-F-02 | 1.1 | Full |
| REQ-F-03 | 1.1 | Full |
| REQ-F-04 | 1.1 | Full |
| REQ-F-05 | 1.1 | Full |
| REQ-F-06 | 1.1 | Full |
| REQ-F-07 | 1.1 | Full |
| REQ-F-08 | 1.1 | Full |
| REQ-NF-01 | 1.1 | Full |
| REQ-NF-02 | 1.1 | Full |
| REQ-NF-03 | 1.1 | Full |
| REQ-NF-04 | 1.1 | Full |
| REQ-NF-05 | 1.1 | Full |
| REQ-NF-06 | All stories (framework-enforced) | Full — `tests/.evals/config.json` thresholds apply automatically to every story's code generation; no dedicated AC needed |
