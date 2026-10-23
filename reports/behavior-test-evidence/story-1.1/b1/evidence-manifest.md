# Evidence Manifest — Behavioural tier B1 (this work unit) — story-1.1

| Field | Value |
|---|---|
| Work unit | Story 1.1 — Upgrade to Premium on the Billing page (frontend only) |
| Branch / head | story/1.1-upgrade-to-premium-on-the-billing-page @ e6aa80b (+ uncommitted story changes) · base e6aa80b |
| Generated | 2026-10-23T15:31:30Z |
| AIRE version | 1.0 |
| Status | PASS |

## Commands run
| # | Command | Working directory | Exit code |
|---|---|---|---|
| 1 | `podman build -t aire-behavior:local -f tests/.evals/behavior/Containerfile .` | repo root | 0 |
| 2 | `MSYS_NO_PATHCONV=1 podman run --rm -v C:/Users/shailendra.yadav/Desktop/projects/helix-aire-v1-demo1/billing-cycle-copy:/work:Z -w /work -e AIRE_STORY_KEY=story-1.1 -e AIRE_BEHAVIOR_REPORT=/work/reports/behavior-test-evidence/story-1.1/b1/behavior-test-report.json aire-behavior:local "bash tests/.evals/behavior/run.sh b1"` | repo root | 0 |

## Tools
| Tool | Version |
|---|---|
| podman | 5.8.7 (machine podman-machine-default, WSL) |
| quickpickle | 1.11.2 |
| vitest | 5.0.5 |
| node (image) | 22.14.0 |

## Result
| Field | Value |
|---|---|
| Tier | B1 (this work unit) |
| Feature files in scope | `spec/behavior/story-1.1.feature` |
| Scenarios passed | 16/16 |
| `@AC` / `@REQ` tags executed | @AC-1..@AC-10: 10/10 |
| Containerised | yes — podman (single container (fake backend modelling the documented /api contract)) |
| Image ref + digest | localhost/aire-behavior:local@sha256:14ad2694b7c2543f70ee9a6f2ef781fb94c4e6ea763535fc8324a86ed5f7ffb3 |

## Artifacts
| File | What it is |
|---|---|
| `behavior-test-run.log` | raw runner output (verbose reporter) |
| `behavior-test-report.json` | Vitest JSON report (machine-readable) |
| `command.txt` | exact podman commands |

## Exceptions and notes
B2 is N/A (no other feature file in spec/behavior/), so no b2/ folder exists. Native debugging runs before the gate surfaced harness defects (QuickPickle pngjs import, AC-10 reporter, lock file ignored) that were fixed before this containerised gate run; the gate passed on its first containerised run (SH-LOOP-7: 0 attempts).
