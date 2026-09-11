# Behavior Test Evidence — B3 (epic scope, last work unit only) — Story 1.1

- **"Last unit" determination**: PR-merge-state, per `common/behavior-spec.md` Section 6.1 — there are no other work units in this cycle at all (single-story epic), so the condition "all others merged" is vacuously satisfied. This IS the last unit.
- **Scope**: B1 (`spec/behavior/story-1.1.feature`, 10 scenarios) union B2 (`spec/behavior.feature`, 0 scenarios) — identical result set to B1.
- **Result**: PASS (same 10/10 as B1 — see `../b1/behavior-test-run.log` and `behavior-test-report.xml`).
- **Containerised**: `false` (same environment reason as B1/B2).
