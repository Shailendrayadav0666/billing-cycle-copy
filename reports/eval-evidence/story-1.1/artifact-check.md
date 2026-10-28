# Artifact Completeness Check — story-1.1

| Field | Value |
|---|---|
| Generated | 2026-10-28T10:38:04Z |
| Attempt | SH-LOOP-16 check 1 (0 remediation attempts used) |
| Result | PASS |

| File | Required because | Present | Format OK | Consistent | Action taken |
|---|---|---|---|---|---|
| `reports/unit-test-evidence/story-1.1/baseline-regression.log` | E1 always | Yes | Yes | Yes | none |
| `reports/unit-test-evidence/story-1.1/unit-test-run.log` | E1 always | Yes | Yes | Yes | none |
| `reports/unit-test-evidence/story-1.1/coverage/lcov.info` | E1 always (machine-readable coverage report) | Yes | Yes | Yes | none |
| `reports/unit-test-evidence/story-1.1/coverage/coverage-summary.json` | E1 always | Yes | Yes | Yes | none |
| `reports/unit-test-evidence/story-1.1/coverage/lcov-report/index.html` | E1 (HTML report emitted by the tool) | Yes | Yes | Yes | none |
| `reports/unit-test-evidence/story-1.1/coverage/changed-lines-coverage.json` | E1 always (gate metric) | Yes | Yes | Yes | none |
| `reports/unit-test-evidence/story-1.1/full-regression.log` | E1 always | Yes | Yes | Yes | none |
| `reports/unit-test-evidence/story-1.1/test-placement-check.log` | E1 (dev-implement, unit changed a test file) | Yes | Yes | Yes | none |
| `reports/unit-test-evidence/story-1.1/evidence-manifest.md` | E1 always | Yes | Yes | Yes | none |
| `reports/behavior-test-evidence/story-1.1/b1/behavior-test-run.log` | E2 b1 always | Yes | Yes | Yes | none |
| `reports/behavior-test-evidence/story-1.1/b1/behavior-test-report.json` | E2 b1 always (machine-readable) | Yes | Yes | Yes | none |
| `reports/behavior-test-evidence/story-1.1/b1/evidence-manifest.md` | E2 b1 always | Yes | Yes | Yes | none |
| `reports/eval-evidence/story-1.1/eval.json` | E6 always | Yes | Yes | Yes | none |
| `reports/eval-evidence/story-1.1/eval-summary.md` | E6 always | Yes | Yes | Yes | none |
| `reports/eval-evidence/story-1.1/static/oxlint.json` | E6 static (post-change output of a D-gate that is not N/A) | Yes | Yes | Yes | none |
| `reports/eval-evidence/story-1.1/static/oxlint-tests.json` | E6 static (post-change output of a D-gate that is not N/A) | Yes | Yes | Yes | none |
| `reports/eval-evidence/story-1.1/static/complexity.json` | E6 static (post-change output of a D-gate that is not N/A) | Yes | Yes | Yes | none |
| `reports/eval-evidence/story-1.1/static/complexity-tests.json` | E6 static (post-change output of a D-gate that is not N/A) | Yes | Yes | Yes | none |
| `reports/eval-evidence/story-1.1/static/semgrep.json` | E6 static (post-change output of a D-gate that is not N/A) | Yes | Yes | Yes | none |
| `reports/eval-evidence/story-1.1/static/npm-audit.json` | E6 static (post-change output of a D-gate that is not N/A) | Yes | Yes | Yes | none |
| `reports/eval-evidence/story-1.1/static/license-report.json` | E6 static (post-change output of a D-gate that is not N/A) | Yes | Yes | Yes | none |
| `reports/eval-evidence/story-1.1/static/gitleaks.json` | E6 static (post-change output of a D-gate that is not N/A) | Yes | Yes | Yes | none |
| `reports/eval-evidence/story-1.1/static/delta-summary.json` | E6 static (post-change output of a D-gate that is not N/A) | Yes | Yes | Yes | none |
| `reports/eval-evidence/story-1.1/static/static-run.log` | E6 static (post-change output of a D-gate that is not N/A) | Yes | Yes | Yes | none |
| `reports/eval-evidence/story-1.1/static/evidence-manifest.md` | E6 static | Yes | Yes | Yes | none |
| `reports/eval-evidence/story-1.1/static/baseline/oxlint.json` | E6 static/baseline (same tool set as post-change) | Yes | Yes | Yes | none |
| `reports/eval-evidence/story-1.1/static/baseline/complexity.json` | E6 static/baseline (same tool set as post-change) | Yes | Yes | Yes | none |
| `reports/eval-evidence/story-1.1/static/baseline/semgrep.json` | E6 static/baseline (same tool set as post-change) | Yes | Yes | Yes | none |
| `reports/eval-evidence/story-1.1/static/baseline/npm-audit.json` | E6 static/baseline (same tool set as post-change) | Yes | Yes | Yes | none |
| `reports/eval-evidence/story-1.1/static/baseline/license-report.json` | E6 static/baseline (same tool set as post-change) | Yes | Yes | Yes | none |
| `reports/eval-evidence/story-1.1/static/baseline/gitleaks.json` | E6 static/baseline (same tool set as post-change) | Yes | Yes | Yes | none |
| `reports/eval-evidence/story-1.1/judge/architecture-score.json` | E6 judge | Yes | Yes | Yes | none |
| `reports/eval-evidence/story-1.1/judge/security-score.json` | E6 judge | Yes | Yes | Yes | none |
| `reports/reviews/story-1.1-code-review-v1.md` | E7 always | Yes | Yes | Yes | none |
| `reports/code-security-reviews/story-1.1-security-review-v1.md` | E8 always | Yes | Yes | Yes | none |
| `runtime-artifacts/stories/story-1.1/audit.md` | E10 always | Yes | Yes | Yes | none |
| `runtime-artifacts/stories/story-1.1/state.md` | E10 always | Yes | Yes | Yes | none |

## N/A gates — no evidence folder

| Gate | Folder | State | Check |
|---|---|---|---|
| behaviorB2 | `reports/behavior-test-evidence/story-1.1/b2` | absent | OK |
| behaviorB3 | `reports/behavior-test-evidence/story-1.1/b3` | absent | OK |
| apiContract | `reports/api-contract-test-evidence/story-1.1` | absent | OK |

N/A reasons (from eval.json):

- D2_types: the frontend is plain JavaScript (.jsx sources, no tsconfig or jsconfig, no TypeScript); no type checker applies to this stack (eval-framework.md Section 2.5.1 reason 1)
- apiContract: the plan has no API Layer Generation step; Story 1.1 adds test tooling and no endpoint
- behaviorB2: no other active feature file: story-1.2 to story-1.6 are Ready for Development and excluded by the activation rule (behavior-spec.md Section 6.0); the repo holds no feature file from an earlier cycle
- behaviorB3: not the last work unit: 1.2, 1.3, 1.4, 1.5 and 1.6 have no merged PR (gh pr list against the epic branch returned no PRs)

Other checks: `reports/playwright-test-evidence/story-1.1` absent; E9 manifest fragment N/A (CI/CD Enabled: No); E11 ticket summary N/A (epic story, not a bug or enhancement unit).
