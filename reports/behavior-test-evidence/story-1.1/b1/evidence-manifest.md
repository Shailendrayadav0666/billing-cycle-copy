# Evidence Manifest — Behavioural B1 — story-1.1

| Field | Value |
|---|---|
| Work unit | Story 1.1 — Frontend unit-test tooling |
| Branch / head | story/1.1-frontend-unit-test-tooling @ 6c0f1a5 (working tree, story changes staged) · base 6c0f1a5 |
| Generated | 2026-10-28T10:25:27Z |
| AIRE version | 1.0 |
| Status | PASS |

## Commands run
| # | Command | Working directory | Exit code |
|---|---|---|---|
| 1 | `podman build -t aire-behavior:local -f tests/.evals/behavior/Containerfile .` | repository root | 0 |
| 2 | `podman run --rm --network none -v "<repo>:/work:Z" -v /work/src/frontend/node_modules -e AIRE_STORY_KEY=story-1.1 aire-behavior:local "bash tests/.evals/behavior/run.sh b1"` | repository root | 0 |

## Tools
| Tool | Version |
|---|---|
| Podman | 5.8.7 (podman-machine-default, WSL) |
| Base image | docker.io/library/node:22.14.0-bookworm |
| Node (in image) | v22.14.0 |
| cucumber-js (in image) | 13.3.0 (pinned in tests/.evals/behavior/package.json and package-lock.json) |
| git (in image) | 2.39.5 |

## Result
| Item | Value |
|---|---|
| Tier | B1 — this unit's own feature file |
| Feature files in scope | spec/behavior/story-1.1.feature |
| Scenarios passed | 5/5 |
| `@AC` tags executed | 4/4 (@AC-1, @AC-2, @AC-3, @AC-4) |
| Containerised | yes — Podman, `--network none` (no request can leave the container) |
| Image ref + digest | localhost/aire-behavior:local · image id sha256:0a587dad61e52ce0f2f998f9ef1a035a58621f9f4408966be37d11346c32a312 · digest sha256:2cb23121b465d80125b826bbab81954b32e0af3c8e19ffa5563ff59db550b78d |
| Pod members | single container (no data store: Story 1.1 has none, and the frontend unit tests mock `/api/billing`) |

| Tags | Scenario | Result | Steps |
|---|---|---|---|
| @AC-1 | Test libraries are added as development dependencies only | PASS | 5/5 steps passed |
| @AC-2 | The unit test command runs a passing Billing page smoke test | PASS | 7/7 steps passed |
| @AC-3 | The coverage command produces a report the coverage gate can read | PASS | 4/4 steps passed |
| @AC-4 | Exact versions are pinned in a committed lock file and audited | PASS | 5/5 steps passed |
| @AC-4 | A high or critical advisory in a new dev dependency is not accepted | PASS | 4/4 steps passed |

## Artifacts
| File | What it is |
|---|---|
| behavior-test-run.log | raw run.sh and cucumber-js output (pretty formatter) |
| behavior-test-report.json | cucumber-js machine-readable report (json formatter) |

## Exceptions and notes
- B2 is N/A: the other feature files (story-1.2 to story-1.6) belong to units that are Ready for Development, so the activation rule (behavior-spec.md Section 6.0) excludes them; `run.sh b2` exited 3 and named each exclusion. No B2 folder exists.
- B3 is N/A: Story 1.1 is not the last work unit. `gh pr list --base epic/HELIX-7344-premium-upgrade-demo-frontend-only --state all` returned no PRs, so 1.2 to 1.6 have no merged PR. No B3 folder exists.
- The AC-2 step runs `npm run test` with extra `--reporter` flags so Vitest also writes a JSON copy of its results; the script and the tests are unchanged by them.
- Bootstrapped by this unit (first in the cycle): tests/.evals/behavior/Containerfile, run.sh, resolve-tier.cjs, package.json, package-lock.json, the root .containerignore, and tests/behavior/steps/ and tests/behavior/support/.
- Self-healing: SH-LOOP-7 used 0 attempts. The image was rebuilt once before this run because the first src/frontend lock file listed only Windows native bindings; that was fixed in the lock file (all versions unchanged, 43 optional platform entries added) before B1 was first run.
