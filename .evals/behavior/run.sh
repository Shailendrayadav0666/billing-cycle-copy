#!/usr/bin/env bash
# Behaviour gate entry point. Runs the Gherkin tiers through pytest-bdd.
#
#   B1 - this work unit's own .feature file
#   B2 - every other work unit's .feature file (accumulated suite)
#   B3 - the cycle-level .spec/behavior.feature (last work unit only)
#
# Select tiers with BEHAVIOR_TIERS, e.g. BEHAVIOR_TIERS=B1,B2  (default)
# Select the current unit with BEHAVIOR_UNIT, e.g. BEHAVIOR_UNIT=story-1.1
#
# Runs identically inside the container (via Containerfile ENTRYPOINT) and natively.
# A missing Podman runtime degrades to native execution: recorded, never blocking.

set -uo pipefail

TIERS="${BEHAVIOR_TIERS:-B1,B2}"
UNIT="${BEHAVIOR_UNIT:-}"
FEATURE_DIR=".spec/aire-docs/implementation/code/behavior"
STEPS_DIR="tests/behavior"
FAILED=0

echo "=== behaviour gate: tiers=$TIERS unit=${UNIT:-<none>} ==="

if [ ! -d "$STEPS_DIR" ]; then
  echo "SKIP: $STEPS_DIR does not exist yet (step definitions are written by dev-implement)."
  echo "Nothing to run. This is not a failure at the STOP CHECKPOINT."
  exit 0
fi

shopt -s nullglob
ALL_FEATURES=("$FEATURE_DIR"/*.feature)
shopt -u nullglob

run_pytest() {
  local label="$1"; shift
  echo "--- $label ---"
  python -m pytest "$STEPS_DIR" -q "$@"
  local rc=$?
  [ $rc -ne 0 ] && [ $rc -ne 5 ] && FAILED=1     # rc 5 = no tests collected, not a failure
  return 0
}

if [[ ",$TIERS," == *",B1,"* ]]; then
  if [ -n "$UNIT" ] && [ -f "$FEATURE_DIR/$UNIT.feature" ]; then
    run_pytest "B1 ($UNIT)" -k "$(echo "$UNIT" | tr '.-' '__')"
  elif [ ${#ALL_FEATURES[@]} -eq 0 ]; then
    echo "B1: no .feature files yet - nothing to run"
  else
    run_pytest "B1 (all units; BEHAVIOR_UNIT unset)"
  fi
fi

if [[ ",$TIERS," == *",B2,"* ]]; then
  if [ ${#ALL_FEATURES[@]} -le 1 ]; then
    echo "B2: fewer than two work-unit feature files - accumulated suite is empty, nothing to add"
  else
    run_pytest "B2 (accumulated suite)"
  fi
fi

if [[ ",$TIERS," == *",B3,"* ]]; then
  if [ -f .spec/behavior.feature ] && grep -qE '^\s*Scenario' .spec/behavior.feature; then
    run_pytest "B3 (cycle-level .spec/behavior.feature)"
  else
    echo "B3: .spec/behavior.feature declares no scenarios."
    echo "    This cycle recorded explicitly that it has no genuine cross-unit journeys"
    echo "    (target_story_count = 1). B3 therefore reduces to B2, which is the correct"
    echo "    outcome and not a gap - see the rationale in .spec/behavior.feature."
  fi
fi

echo "=== behaviour gate: $([ $FAILED -eq 0 ] && echo PASS || echo FAIL) ==="
exit $FAILED
