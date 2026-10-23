# Code Security Review Report

**Date**: 2026-10-23
**Reviewer**: AI Security Audit (AIRE Security Baseline)
**Rules Source**: `aire-workflow/extensions/security/baseline/security-baseline.md`
**Project**: Billing-Cycle (StreamPlex), Story 1.1 Upgrade to Premium on the Billing page (frontend only)
**Tech Stack**: React 19 + Vite 8 SPA (`src/frontend`); FastAPI backend (`src/backend`, unchanged)
**Scan Scope**: This work unit's diff (`story/1.1-upgrade-to-premium-on-the-billing-page` vs `e6aa80b`) and the attack surface it reaches: `src/frontend/src/pages/Billing.jsx`, `src/frontend/src/App.css`, `src/frontend/package.json` + `package-lock.json`, `src/frontend/.gitignore`, `src/frontend/vitest*.js`, `tests/unit/**`, `tests/behavior/**`, `tests/.evals/**`
**Review version**: v1 (pairs with `reports/reviews/story-1.1-code-review-v1.md`)

---

## Executive Summary

- **Total Findings**: 0 on the changed surface (blocking: 0) · 3 advisory items (1 Low on the change, 2 pre-existing)
- **Critical/Blocker**: 0
- **High**: 0 (on this change; 2 pre-existing High dependency advisories are listed under Advisory)
- **Medium**: 0
- **Low**: 1 (advisory, dev-only dependency)
- **Security Rules Checked**: 16/16
- **Rules Compliant**: 5/16
- **Rules Non-Compliant**: 0/16
- **Rules N/A**: 11/16
- **Overall Risk Rating**: Low

---

## Findings Summary Table

| # | Severity | Security Rule | Title | File(s) | Line(s) |
|---|----------|--------------|-------|---------|---------|
| 1 | Low (advisory) | SECURITY-10 | Dev-only transitive `uuid` < 11.1.1 (GHSA-w5hq-g745-h8pq) via quickpickle → @cucumber/messages; no fix available | `src/frontend/package-lock.json` | `node_modules/uuid` entry |

---

## Critical / Blocker Findings

None.

---

## High Findings

None on the changed surface.

---

## Medium Findings

None.

---

## Low Findings

### [SEC-ADV-001] Dev-only transitive uuid advisory
- **Severity**: Low (advisory, not blocking)
- **Security Rule**: SECURITY-10 — Software Supply Chain Security
- **Verification Criteria Violated**: none. Dependencies are exact-pinned, the lock file is committed, sources are official, and the scanner ran. This is a known advisory in a transitive dependency.
- **File(s)**: `src/frontend/package-lock.json` (`node_modules/uuid`, reached via `quickpickle` → `@cucumber/gherkin` / `@cucumber/messages`)
- **Description**: `npm audit` reports GHSA-w5hq-g745-h8pq (uuid: missing buffer bounds check in v3/v5/v6 when `buf` is provided), rated moderate, with no fix available upstream.
- **Evidence**: `reports/eval-evidence/story-1.1/static/npm-audit.json`. The four moderate entries (`uuid`, `@cucumber/messages`, `@cucumber/gherkin`, `quickpickle`) all stem from this one advisory.
- **Impact**: none in production. The package is a devDependency of the Gherkin test runner, is not in the `vite build` bundle, and the runner never calls uuid with a caller-supplied buffer.
- **Remediation**: upgrade quickpickle when @cucumber/messages ships with uuid ≥ 11.1.1. Track it with `/raise-defect` if desired.
- **References**: CWE-787; OWASP A03:2025

---

## Security Baseline Compliance Matrix

| Security Rule | Rule Name | Status | Findings |
|---|---|---|---|
| SECURITY-01 | Encryption at Rest and in Transit | N/A: the diff adds no data store or transport | 0 |
| SECURITY-02 | Access Logging on Network Intermediaries | N/A: no load balancer, gateway or CDN in the diff | 0 |
| SECURITY-03 | Application-Level Logging | N/A: no logging added or changed (no `console.*` in the diff) | 0 |
| SECURITY-04 | HTTP Security Headers | N/A: no server or HTTP header configuration changed | 0 |
| SECURITY-05 | Input Validation | N/A: no API parameter or user input handled. The upgrade takes no input (`Billing.jsx:119-122`). | 0 |
| SECURITY-06 | Least-Privilege Access Policies | N/A: no IAM or policy in the diff | 0 |
| SECURITY-07 | Restrictive Network Configuration | N/A: no network configuration in the diff | 0 |
| SECURITY-08 | Application-Level Access Control | N/A: `ProtectedRoute`, `AuthContext` and backend routes are unchanged | 0 |
| SECURITY-09 | Security Hardening | Compliant: test configs (`vitest*.js`) are not used by `vite build` or the dev server, and no debug or default-credential change ships | 0 |
| SECURITY-10 | Software Supply Chain Security | Compliant: 9 devDependencies exact-pinned (`package.json`), `package-lock.json` now tracked (removed from `.gitignore`), all resolved from `https://registry.npmjs.org/`, `npm audit` run | 0 (1 advisory) |
| SECURITY-11 | Secure Design Principles | Compliant: the upgrade is client-only and grants nothing server-side (no privilege or entitlement is changed). Plan data is display state only. | 0 |
| SECURITY-12 | Authentication and Credential Management | N/A: no auth or credential code changed. Test fixtures use the documented demo account only, in `tests/**`. | 0 |
| SECURITY-13 | Software and Data Integrity | Compliant: the lock file carries `integrity` (sha512) hashes for every added package | 0 |
| SECURITY-14 | Alerting and Monitoring | N/A: no monitoring surface in the diff | 0 |
| SECURITY-15 | Exception Handling and Fail-Safe Defaults | Compliant: `handleUpgrade` (`Billing.jsx:119-122`) runs only after data has loaded (the button renders only when `data` exists, line 170), and it cannot throw on loaded data | 0 |
| SECURITY-16 | Cryptographic Standards and Certificate Validation | N/A: no cryptography or TLS in the diff | 0 |

---

## OWASP Reference Mapping

| Item | OWASP 2025 |
|---|---|
| SEC-ADV-001 | A03:2025 Software Supply Chain Failures |

---

## Recommendations Priority

### Immediate (Blocks Deployment)
None.

### Short-Term (Current Sprint)
None for this change.

### Medium-Term (Current Release)
1. Pre-existing (not this change): upgrade `vite` beyond 8.3.2 and `source-map-js` beyond 1.2.1. Both have High dependency advisories in the baseline `npm audit` (`static/baseline/npm-audit.json`), and a fix is available. Recommend `/raise-defect`.

### Long-Term (Backlog)
1. SEC-ADV-001: bump quickpickle once upstream ships uuid ≥ 11.1.1.
2. Pre-existing auth weaknesses recorded by the Atlas deep dive (email used as token, token in `localStorage` and in the query string) are out of scope and not touched by this change.

---

## Appendix

### Methodology
- Manual review of the work unit's diff against the AIRE Security Baseline (SECURITY-01 through SECURITY-16), each rule's verification criteria
- Rules source: `aire-workflow/extensions/security/baseline/security-baseline.md`
- Tool evidence reused, not re-run: `reports/eval-evidence/story-1.1/static/` (semgrep p/javascript and p/react: 0 findings; gitleaks: no leaks; npm audit; license-checker)

### Excluded from Scope
- Files this work unit did not change (diff-scoped run); pre-existing items are listed only as advisory
- `src/backend/**` (unchanged, per REQ-NF-01)
