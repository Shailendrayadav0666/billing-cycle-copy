# Artifact Completeness Check — story-1.1

**Result**: PASS · SH-LOOP-16 attempt 0 (no fix needed)

| File | Required because | Present | Format OK | Consistent | Action taken |
|---|---|---|---|---|---|
| `reports/unit-test-evidence/story-1.1/baseline-regression.log` | E1 always | yes | yes | yes | none |
| `reports/unit-test-evidence/story-1.1/unit-test-run.log` | E1 always | yes | yes | yes | none |
| `reports/unit-test-evidence/story-1.1/coverage/lcov.info` | E1 coverage report | yes | yes | yes | none |
| `reports/unit-test-evidence/story-1.1/coverage/changed-lines-coverage.json` | E1 gate metric | yes | yes | yes | none |
| `reports/unit-test-evidence/story-1.1/full-regression.log` | E1 always | yes | yes | yes | none |
| `reports/unit-test-evidence/story-1.1/test-placement-check.log` | E1 test files changed | yes | yes | yes | none |
| `reports/unit-test-evidence/story-1.1/evidence-manifest.md` | E1 always | yes | yes | yes | none |
| `reports/behavior-test-evidence/story-1.1/b1/behavior-test-run.log` | E2 b1 always | yes | yes | yes | none |
| `reports/behavior-test-evidence/story-1.1/b1/behavior-test-report.json` | E2 b1 always | yes | yes | yes | none |
| `reports/behavior-test-evidence/story-1.1/b1/evidence-manifest.md` | E2 b1 always | yes | yes | yes | none |
| `reports/behavior-test-evidence/story-1.1/b3/behavior-test-run.log` | E2 b3 ran (last unit) | yes | yes | yes | none |
| `reports/behavior-test-evidence/story-1.1/b3/behavior-test-report.json` | E2 b3 ran (last unit) | yes | yes | yes | none |
| `reports/behavior-test-evidence/story-1.1/b3/evidence-manifest.md` | E2 b3 ran (last unit) | yes | yes | yes | none |
| `reports/eval-evidence/story-1.1/eval.json` | E6 always | yes | yes | yes | none |
| `reports/eval-evidence/story-1.1/eval-summary.md` | E6 always | yes | yes | yes | none |
| `reports/eval-evidence/story-1.1/static/evidence-manifest.md` | E6 D-gates ran | yes | yes | yes | none |
| `reports/eval-evidence/story-1.1/judge/architecture-score.json` | E6 J1 PASS | yes | yes | yes | none |
| `reports/eval-evidence/story-1.1/judge/security-score.json` | E6 J2 | yes | yes | yes | none |
| `reports/reviews/story-1.1-code-review-v1.md` | E7 always | yes | yes | yes | none |
| `reports/code-security-reviews/story-1.1-security-review-v1.md` | E8 always | yes | yes | yes | none |
| `runtime-artifacts/stories/story-1.1/audit.md` | E10 always | yes | yes | yes | none |
| `runtime-artifacts/stories/story-1.1/state.md` | E10 always | yes | yes | yes | none |

## Consistency rules (work-unit-artifacts.md Section 4)

| Rule | Holds |
|---|---|
| b2/ absent for N/A behaviorB2 | yes |
| api-contract folder absent for N/A apiContract | yes |
| no playwright evidence folder | yes |
| static/baseline outputs >= D-gates that ran (6) | yes |
| review names security report v1 and J1/J2 match judge/*.json | yes |
| unitCoverage value == changed-lines-coverage.json | yes |
| eval.json verdict PASS | yes |

## N/A gates

| Gate | Reason |
|---|---|
| D2_types | src/frontend is plain JavaScript/JSX with no TypeScript and no type checker in its toolchain; type checking cannot apply to this stack (closed-list reason 1) |
| behaviorB2 | spec/behavior/ holds no feature file other than this unit's own story-1.1.feature (single-story epic) |
| apiContract | the code-generation plan has no API Layer Generation step; no endpoint is added or changed (REQ-NF-01) |
