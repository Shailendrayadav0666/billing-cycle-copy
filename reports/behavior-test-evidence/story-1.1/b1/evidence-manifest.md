# Behavior Test Evidence — B1 (this unit's own contract) — Story 1.1

- **Command**: `pytest tests/behavior/steps/test_story_1_1.py -v --junitxml=behavior-test-report.xml`
- **Feature file**: `spec/behavior/story-1.1.feature` (the stem `story-1.1` matches this work unit's own key)
- **Containerised**: `false` — `"reason": "podman machine has no outbound network access to docker.io (verified, not transient)"` (recorded user-approved deviation, `runtime-artifacts/aire-state.md` Environment Notes)
- **Result**: 10/10 scenarios PASS, every `@AC1`..`@AC9`/`@AC8b` tag executed
- **Raw log**: `behavior-test-run.log`
- **Machine-readable report**: `behavior-test-report.xml` (JUnit)
