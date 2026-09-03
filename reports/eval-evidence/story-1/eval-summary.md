# Eval Scorecard — Story 1: Mid-Cycle Subscription Upgrade (Standard → Premium)

| Gate | Result |
|---|---|
| D1 Lint | PASS (0 new findings) |
| D2 Types | PASS (0 new findings) |
| D3 SAST | PASS (0 new findings) |
| D4 Dependencies | PASS |
| D5 Licences | N/A (no dependency changes) |
| D6 Complexity | PASS |
| D7 Secrets | PASS |
| Unit Coverage | **PASS — 100%** on new/changed code (threshold 90%) |
| Behaviour B1 | PASS — 9/9 scenarios |
| Behaviour B2 | N/A — no other feature file yet |
| Behaviour B3 | PASS — 11/11 scenarios (single-unit cycle) |
| API & Contract | PASS — 12/12 checklist items |
| Full Regression | PASS — 36/36, 0 new failures |
| J1 Architecture | **1.00** / 0.85 minimum — PASS |
| J2 Security | **1.00** / 0.85 minimum — PASS |
| Code Review | Clean (v2) — 1 remediation round (AC-6 fix) |

**Overall verdict: PASS.** All gates green; 0 outstanding findings.

Note: D7 and the Behaviour tiers ran natively (not in Podman) on this local Windows dev machine — `podman machine start` failed twice (WSL2 VM transition error), not "Podman not installed". The epic-level pre-handoff smoke test already proved the identical containerised path works correctly in the real CI environment (GitHub Actions, PR #5, run 33745286732), so this PR's own CI run is expected to execute these tiers inside Podman as designed.
