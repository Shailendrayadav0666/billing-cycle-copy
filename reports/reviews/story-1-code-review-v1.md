# Code Review — Story 1: Mid-Cycle Subscription Upgrade (Standard → Premium)

**Version**: v1
**Reviewer role**: automated Code Review (read-only) per `workflows/code-review.md`
**Scope**: this story's diff only (`src/backend/main.py`, `src/frontend/src/pages/Billing.jsx`, `src/frontend/src/App.css`)

## Tests Reviewed / Coverage (reused from dev-implement evidence, not re-run)
- Unit: `tests/unit/test_billing_upgrade.py` — 13/13 passed, 100% coverage on new/changed code (`reports/unit-test-evidence/story-1/`)
- API & Contract: `tests/unit/test_billing_upgrade_contract.py` — 12/12 passed, full checklist (`reports/api-contract-test-evidence/story-1/`)
- Behaviour: B1 9/9, B3 11/11 (`reports/behavior-test-evidence/story-1/`)
- Full regression: 36/36, 0 new failures vs baseline (`reports/unit-test-evidence/story-1/full-regression.log`)

## AC / Requirement Compliance Check

| AC | Covers | Status |
|---|---|---|
| AC-1 | REQ-F-01, F-02, F-03 | Met |
| AC-2 | REQ-F-04, F-05, F-07, NF-01 | Met |
| AC-3 | REQ-F-08 | Met |
| AC-4 | REQ-F-09, NF-02, NF-03 | Met |
| AC-5 | REQ-F-10, F-11, F-14, F-15, F-17 | Met |
| **AC-6** | **REQ-F-12** | **Partially Met** |
| AC-7 | REQ-F-13, NF-04 | Met |
| AC-8 | REQ-F-16 | Met |
| AC-9 | REQ-F-18, NF-05 | Met |

## Findings

### 🟠 ISS-001 — AC-6 partially met: modal does not auto-close on successful upgrade
- **AC-6 requires**: "the frontend MUST re-fetch `GET /api/billing`, **close the modal**, hide the upgrade CTA, and show a success banner"
- **Found**: `Billing.jsx`'s `confirmUpgrade()` set a success message rendered **inside** the still-open modal, requiring the user to click an extra "Close" button. The modal was not auto-closed and the banner was not shown on the page itself.
- **Severity**: 🟠 High (AC partially met — the re-fetch, hide-CTA and success-message parts were correct; only the auto-close/banner-placement part deviated)

## Security Baseline Review (Phase 2.5, diff-scoped)
Reviewed the diff against the 16 Security Baseline rules (SECURITY-01..16), scoped to `src/backend/main.py` (new endpoints) and `src/frontend/src/pages/Billing.jsx`:
- No secrets, tokens, or PII written to logs (no new logging added).
- No new input trusted without validation — both endpoints validate via Pydantic (`UpgradeRequest`) / FastAPI query param typing; the `email` is checked against `users` before any billing mutation (existing pattern).
- No new external network call (`charge_card` is in-process only) — no SSRF surface introduced.
- Error responses (`402`, `409`) disclose no internal state beyond the documented `detail`/`message` fields.
- No new dependency added (REQ-NF-03) — nothing to assess for supply-chain risk.
- **Pre-existing, out of scope**: the wildcard CORS (`allow_origins=["*"]`) at `main.py:14` and the email-as-bearer-token auth pattern are pre-existing design choices this story did not introduce or touch — noted as **advisory**, not a finding (per the diff-scoped rule).
- **No 🔴 Critical / 🟠 High Security Baseline finding on the changed surface.**

## Verdict
**Findings: 🔴 0 🟠 1 (ISS-001)** → routes to Auto-Remediate (SH-LOOP-5, round 1 of 3).
