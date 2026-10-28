# Code Security Review Report

**Date**: 2026-10-28
**Reviewer**: AI Security Audit (AIRE Security Baseline)
**Rules Source**: `aire-workflow/extensions/security/baseline/security-baseline.md`
**Project**: billing-cycle-copy (StreamPlex billing demo)
**Tech Stack**: React 19 + Vite 8 frontend (`src/frontend`, plain JavaScript); FastAPI backend (`src/backend`, unchanged); new test tooling: Vitest 5, React Testing Library 16, jsdom 29; behaviour runner cucumber-js 13 in Podman
**Scan Scope**: This work unit's diff and the attack surface it reaches (diff-scoped run) — Story 1.1, branch `story/1.1-frontend-unit-test-tooling`, base 6c0f1a5
**Code Review version**: v1

---

## Executive Summary

- **Total Findings**: 0 on the changed surface (Critical 0, High 0, Medium 0, Low 0)
- **Advisory, not findings**: 2 pre-existing High dependency advisories; 3 Low observations on test-only infrastructure and documentation
- **Security Rules Checked**: 16/16
- **Rules Compliant**: 4/16 (SECURITY-09, SECURITY-10, SECURITY-12, SECURITY-13 on the changed surface)
- **Rules Non-Compliant**: 0/16
- **Rules N/A**: 12/16
- **Overall Risk Rating**: Low

Attack surface reached by the diff: none at run time. The diff adds development and test tooling (dev dependencies, a test-only Vitest configuration, a unit test, behaviour step definitions, a test container image) and commits the frontend lock file. No application source under `src/frontend/src`, no backend file, no route, no request path and no production build setting changes.

---

## Findings Summary Table

| # | Severity | Security Rule | Title | File(s) | Line(s) |
|---|----------|--------------|-------|---------|---------|
| — | — | — | No findings on the changed surface | — | — |

---

## Critical / Blocker Findings

None.

---

## High Findings

None on the changed surface. See Pre-existing (advisory) below.

---

## Medium Findings

None.

---

## Low Findings

None as findings. The Low observations below are advisory.

### Pre-existing (advisory, not this change)

- **ADV-01 — vite 8.3.0 dev-server advisories (npm audit: high)** · SECURITY-10 · `src/frontend/package-lock.json:2224`
  GHSA-587h-7wmj-h5pm (high, launch-editor existence check bypass on Windows), GHSA-698v-4r3x-3vcv and GHSA-r825-w8mm-5pxw (moderate, launch-editor), GHSA-rq7h-c2jc-7f22 and GHSA-vfpm-58rq-9qcg (moderate, dev server file exposure), GHSA-9jrq-w75r-8gcw (low). vite was already a dev dependency at 8.3.0 before this unit, and the same advisories were in the baseline audit. They affect the development server only, not the production build. This unit commits the lock file for the first time, so `npm ci` now installs 8.3.0 consistently. Fix available: vite 8.3.5. Recommend `/raise-defect`.
- **ADV-02 — source-map-js 1.2.1 (npm audit: high)** · SECURITY-10 · transitive (vite and postcss)
  GHSA-68fv-2mgg-jv7q (event-loop denial of service through indexed source-map section offsets). Present at the baseline. Fix available: 1.2.2. Recommend `/raise-defect` together with ADV-01.

### Low observations on test-only infrastructure (advisory)

- **ADV-03 — the behaviour image runs as root** · SECURITY-09 · `tests/.evals/behavior/Containerfile:5`
  SECURITY-09's container hardening applies to deployed components; this image is test infrastructure and is never deployed. It runs under rootless Podman with `--network none` and a bind-mounted checkout. A non-root `USER` would lose write access to the bind mount (reports, coverage) under rootless user mapping.
- **ADV-04 — base image pinned by tag, not digest** · SECURITY-13 · `tests/.evals/behavior/Containerfile:5`
  `node:22.14.0-bookworm` is an exact version tag (not `latest`); Podman verifies layer digests on pull. Pinning by digest would make the test image fully reproducible.
- **ADV-05 — `npm audit` is not named in the frontend build instructions** · SECURITY-10 · `src/frontend/README.md`
  The scan ran and its result is recorded (REQ-NF-06). The project has no CI pipeline (opted out), so the documented step would be the README.

---

## Security Baseline Compliance Matrix

| Security Rule | Rule Name | Status | Findings |
|---|---|---|---|
| SECURITY-01 | Encryption at Rest and in Transit | N/A — no data store, transport or storage configuration in the diff | 0 |
| SECURITY-02 | Access Logging on Network Intermediaries | N/A — no load balancer, gateway or CDN | 0 |
| SECURITY-03 | Application-Level Logging | N/A — no application logging added or changed | 0 |
| SECURITY-04 | HTTP Security Headers | N/A — no server or HTML-serving change (vite.config.js and index.html unchanged) | 0 |
| SECURITY-05 | Input Validation | N/A — no API parameter or input handling in the diff | 0 |
| SECURITY-06 | Least-Privilege Access Policies | N/A — no IAM or policy | 0 |
| SECURITY-07 | Restrictive Network Configuration | N/A — no network configuration (the test container runs with `--network none`) | 0 |
| SECURITY-08 | Application-Level Access Control | N/A — no route, guard or data access changes | 0 |
| SECURITY-09 | Security Hardening | Compliant — no default credentials, no debug endpoints, production build unchanged; test image advisory ADV-03 | 0 |
| SECURITY-10 | Software Supply Chain Security | Compliant — lock file committed (`src/frontend/package-lock.json`), every added package from registry.npmjs.org with sha512 integrity, dev-only, `npm audit` run and recorded, no `latest` image tags; pre-existing advisories ADV-01 and ADV-02 | 0 |
| SECURITY-11 | Secure Design Principles | N/A — no design-level change to the application | 0 |
| SECURITY-12 | Authentication and Credential Management | Compliant — no credential added; gitleaks on the staged diff found 0; the test uses only the demo account email as a mocked token | 0 |
| SECURITY-13 | Software and Data Integrity | Compliant — `npm ci` verifies integrity hashes for the app and the behaviour runner (both locks committed); no deserialisation of untrusted input, no XML parsing, no CDN script; advisory ADV-04 | 0 |
| SECURITY-14 | Alerting and Monitoring | N/A — no deployed component | 0 |
| SECURITY-15 | Exception Handling and Fail-Safe Defaults | N/A — no external call or error path in application code changes (Billing.jsx's fetch is changed in Story 1.3) | 0 |
| SECURITY-16 | Cryptographic Standards and Certificate Validation | N/A — no cryptography or TLS configuration | 0 |

---

## OWASP Reference Mapping

| Item | OWASP Top 10:2025 |
|---|---|
| ADV-01, ADV-02, ADV-05 (SECURITY-10) | A03 Software Supply Chain Failures |
| ADV-03 (SECURITY-09) | A02 Security Misconfiguration |
| ADV-04 (SECURITY-13) | A08 Software or Data Integrity Failures |

---

## Recommendations Priority

### Immediate (Blocks Deployment)
None.

### Short-Term (Current Sprint)
1. Raise a defect to update vite to 8.3.5 or later and source-map-js to 1.2.2 or later (ADV-01, ADV-02); both are pre-existing.

### Medium-Term (Current Release)
None.

### Long-Term (Backlog)
1. Pin the behaviour image's base by digest (ADV-04).
2. Name `npm audit` in the frontend build instructions (ADV-05).

---

## Appendix

### Methodology
- Diff-scoped review against AIRE Security Baseline (SECURITY-01 through SECURITY-16); every rule checked against the files this unit added or changed.
- Rules source: `aire-workflow/extensions/security/baseline/security-baseline.md`.
- Inputs: `git diff --cached 6c0f1a5` (staged story changes), `reports/eval-evidence/story-1.1/npm-audit-install.json`, `reports/eval-evidence/story-1.1/static/` (semgrep, gitleaks, npm audit, licences).

### Excluded from Scope
- Files this unit did not touch (all of `src/frontend/src`, `src/backend`). Pre-existing issues there belong to the standalone `code-security-review` audit.
- Generated evidence under `reports/`.
