# Eval Scorecard — Story 1.1 (Mid-Cycle Subscription Upgrade)

**Overall: PASS** (14 of 14 local checks ran — 0 N/A)

| Gate | Result | Detail |
|---|---|---|
| D1 Lint | PASS | 3 new findings introduced and fixed in this run (backend E501 x2, frontend exhaustive-deps x1); 5 pre-existing findings untouched |
| D2 Type check | PASS | 3 new mypy errors introduced and fixed in this run (`PLANS`/`renew_at` typing); 2 pre-existing errors untouched |
| D3 SAST | PASS | 0 new findings (semgrep); 1 pre-existing WARNING (`wildcard-cors`, out of scope) |
| D4 Dependencies | PASS | 0 vulnerabilities in new backend deps (pip-audit); 6 pre-existing frontend vulnerabilities untouched |
| D5 Licenses | PASS | 0 flagged (backend + frontend) |
| D6 Complexity | PASS | max cyclomatic complexity on changed functions: 3 (threshold 12) |
| D7 Secrets | PASS | 0 leaks (gitleaks) |
| Unit Test & Coverage | PASS | 15/15 tests passing (8 backend + 7 frontend); **100% coverage of new/changed code** both stacks |
| API & Contract | PASS | both new endpoints: functional, response codes, error shape, request/response contract all verified; role-based auth N/A (no role model anywhere in this codebase) |
| Behavior B1 | PASS | native execution (`"containerised": false, "reason": "podman machine has no outbound network access to docker.io (verified, not transient)"`); pytest-bdd, `tests/behavior/steps/test_story_1_1.py` — 10/10 scenarios pass, every `@AC-n` tag executed |
| Behavior B2 | PASS | native (same reason); repo's only other feature file (`spec/behavior.feature`) has no scenarios — vacuously green |
| Behavior B3 | PASS | native (same reason); last (only) work unit by PR-merge-state — B3 = B1 union B2 plus `spec/behavior.feature`'s cross-unit journeys (none recorded) |
| J1 Architecture | **1.00** / 0.85 min | all 5 constraints score 1.0 — see `judge/architecture-score.json` |
| J2 Security | **1.00** / 0.85 min | all 4 OWASP criteria score 1.0 — see `judge/security-score.json` |

**Self-healing loops used**: 0 remediation rounds needed against a committed baseline (SH-LOOP-4/5). The D1/D2/D6 static-eval and D1-frontend findings above were introduced and fixed inline during the SAME code-generation pass, before any commit or review.

**SonarQube**: not a local gate — `common/eval-framework.md` Section 5 gate inventory records it as CI-only. It runs for real on this story's PR and is cross-checked against this scorecard by the CI Attestation Gate.
