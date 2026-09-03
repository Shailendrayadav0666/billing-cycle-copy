# B3 Evidence — Epic scope (single-unit cycle)

**Trigger**: single-unit cycle (Story 1 IS the whole epic, per the user's explicit single-story override — see `spec/plans/stories.md` granularity note). Per `common/behavior-spec.md` Section 6.1: "there are no other units, so the condition is satisfied immediately and B3 runs on that unit." Recorded as run on a single-unit cycle, not presented as skipped.
**Scope**: B1 (`spec/behavior/story-1.feature`, 9 scenarios) union B2 (none) plus the cross-unit journeys in `spec/behavior.feature` (2 scenarios, tagged `@REQ-*`).
**Command**: `src/backend/venv/Scripts/python.exe -m pytest tests/behavior/ -v --junitxml=.../behavior-test-report.xml`
**Result**: 11/11 scenarios passed — every `@REQ-<id>` the cycle covers is executed.
**Containerised**: `false` — same reason as B1 (Podman machine failed to start on this Windows host); CI already proved the real container path works (PR #5).
**Artifacts**: `behavior-test-run.log`, `behavior-test-report.xml`.
