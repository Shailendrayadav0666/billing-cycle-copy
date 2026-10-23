# Evidence Manifest — Behavioural tier B3 (epic scope — last/only work unit) — story-1.1

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
| 2 | `podman pod create --name aire-beh` | repo root | 0 |
| 3 | `podman run -d --pod aire-beh --name beh-api -v C:/Users/shailendra.yadav/Desktop/projects/helix-aire-v1-demo1/billing-cycle-copy:/work:Z,ro docker.io/library/python:3.11-slim sh -c "pip install --no-cache-dir -q -r /work/src/backend/requirements.txt && cd /tmp && uvicorn main:app --app-dir /work/src/backend --host 127.0.0.1 --port 8000"` | repo root | 0 |
| 4 | `podman run --rm --pod aire-beh -v C:/Users/shailendra.yadav/Desktop/projects/helix-aire-v1-demo1/billing-cycle-copy:/work:Z -w /work -e AIRE_STORY_KEY=story-1.1 -e AIRE_BACKEND_URL=http://127.0.0.1:8000 -e AIRE_BEHAVIOR_REPORT=/work/reports/behavior-test-evidence/story-1.1/b3/behavior-test-report.json aire-behavior:local "bash tests/.evals/behavior/run.sh b3"` | repo root | 0 |
| 5 | `podman pod rm -f aire-beh` | repo root | 0 |

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
| Tier | B3 (epic scope — last/only work unit) |
| Feature files in scope | `spec/behavior/story-1.1.feature`, `spec/behavior.feature` |
| Scenarios passed | 17/17 |
| `@AC` / `@REQ` tags executed | @AC-1..@AC-10: 10/10 · @REQ-F-01, @REQ-F-03, @REQ-F-10, @REQ-NF-01, @REQ-NF-02: 5/5 |
| Containerised | yes — podman (pod aire-beh: beh-api (docker.io/library/python:3.11-slim@sha256:b95327ce1439e687237841b0210677aeadd62d55a060a5f6bcb9c15bf6251dd3, real FastAPI src/backend on 127.0.0.1:8000) + test container; torn down after the run) |
| Image ref + digest | localhost/aire-behavior:local@sha256:14ad2694b7c2543f70ee9a6f2ef781fb94c4e6ea763535fc8324a86ed5f7ffb3 |

## Artifacts
| File | What it is |
|---|---|
| `behavior-test-run.log` | raw runner output (verbose reporter) |
| `behavior-test-report.json` | Vitest JSON report (machine-readable) |
| `command.txt` | exact podman commands |
| `backend.log` | tail of the FastAPI access log for the run |

## Exceptions and notes
Single-story epic: no other work unit exists, so this unit is the last and B3 runs (behavior-spec.md Section 6.1). The backend access log shows no request between the Billing load and the reload (AC-7 / REQ-NF-01). SH-LOOP-8: 0 attempts.
