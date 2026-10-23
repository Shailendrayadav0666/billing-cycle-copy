### Eval Scorecard — Story 1.1 · **PASS**

| Gate | Result | Threshold | Status |
|---|---|---|---|
| D1 Lint | 0 new findings (3 pre-existing warnings in AuthContext.jsx) | ≤ 0 delta | PASS |
| D2 Type check | plain JavaScript/JSX root, no type checker applies | 0 | N/A |
| D3 Static security | 0C / 0H / 0M new | 0C / 0H / ≤5M | PASS |
| D4 Dependencies | 0C / 0H new (4 moderate, dev-only) | 0C / 0H | PASS |
| D5 Licences | 0 violations (144 packages) | none disallowed | PASS |
| D6 Complexity | 0 functions over threshold | ≤ 12 | PASS |
| D7 Secrets | 0 findings | 0 | PASS |
| Unit coverage | 100.0% changed lines · 100.0% changed branches · 15/15 tests | ≥ 90.0% | PASS |
| Behavioural B1 (this story) | 16/16 scenarios · 10/10 ACs · podman | 100% | PASS |
| Behavioural B2 (cumulative) | no other feature file in spec/behavior/ (single-story epic) | other units only | N/A |
| Behavioural B3 (epic scope) | 17/17 scenarios · 2 feature files · 5/5 @REQ tags · podman pod with real backend | 100% | PASS |
| API & contract | plan has no API Layer Generation step | all applicable | N/A |
| Regression | 0 new failures (15/15; baseline 0 tests) | 0 | PASS |
| J1 Architecture | 1.00 | ≥ 0.85 | PASS |
| J2 Security (OWASP 2025) | 1.00 | ≥ 0.85 | PASS |

**Verdict**: PASS · judge `claude-opus-5-5` · rubric v1.0.0 (from `architecture.md` v1.0.0)
**Self-healing**: SH-LOOP-1 2/3 · all other loops 0/3

**J1 breakdown**: ARCH-01 0.25 → 1.0 · ARCH-02 0.2 → 1.0 · ARCH-03 0.15 → 1.0 · ARCH-04 0.1 → 1.0 · ARCH-05 0.15 → 1.0 · ARCH-06 0.15 → 1.0
**J2 breakdown**: SEC-01 (A03:2025) 0.25 → 1.0 · SEC-02 (A05:2025) 0.2 → 1.0 · SEC-03 (A07:2025) 0.15 → 1.0 · SEC-04 (A01:2025) 0.1 → N/A · SEC-05 (A02:2025) 0.1 → 1.0 · SEC-06 (A09:2025) 0.1 → 1.0 · SEC-07 (A10:2025) 0.1 → 1.0
**Bootstrapped**: tests/.evals/eslint-complexity.config.mjs (D6), tests/.evals/gitleaks.toml (D7), tests/.evals/behavior/Containerfile + run.sh (behaviour runner)
