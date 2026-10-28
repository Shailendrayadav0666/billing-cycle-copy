#!/usr/bin/env bash
# AIRE behavioural gate entry point (aire-workflow/common/behavior-spec.md Sections 5 and 6).
# The developer, AIRE and CI all run it the same way, inside the aire-behavior:local image:
#
#   podman build -t aire-behavior:local -f tests/.evals/behavior/Containerfile .
#   podman run --rm --network none -v "<repo>:/work:Z" -v /work/src/frontend/node_modules \
#     -e AIRE_STORY_KEY=<unit-key> aire-behavior:local "bash tests/.evals/behavior/run.sh <b1|b2|b3>"
#
# The anonymous volume on /work/src/frontend/node_modules keeps the image's Linux dependencies in
# place of the host's copy. Pass the run.sh command as ONE quoted string (ENTRYPOINT is sh -c).
#
# Exit codes: 0 all scenarios passed · 1 a scenario failed · 2 usage or setup error ·
#             3 the tier has no active feature files (record the tier as N/A).
set -euo pipefail

TIER="${1:-}"
case "$TIER" in
  b1|b2|b3) ;;
  *) echo "run.sh: no tier supplied (expected b1, b2 or b3)" >&2; exit 2 ;;
esac

KEY="${AIRE_STORY_KEY:-}"
if [ -z "$KEY" ]; then
  echo "run.sh: AIRE_STORY_KEY is not set, so B1 cannot tell which work unit is under test" >&2
  exit 2
fi

cd "$(dirname "$0")/../../.."

set +e
FEATURES="$(node tests/.evals/behavior/resolve-tier.cjs "$TIER" "$KEY")"
RESOLVE_EXIT=$?
set -e
[ "$RESOLVE_EXIT" -eq 0 ] || exit "$RESOLVE_EXIT"
if [ -z "$FEATURES" ]; then
  echo "run.sh: tier $TIER has no active feature files for $KEY - record the tier as N/A"
  exit 3
fi

OUT="reports/behavior-test-evidence/$KEY/$TIER"
mkdir -p "$OUT"
exec > >(tee "$OUT/behavior-test-run.log") 2>&1

echo "tier=$TIER unit=$KEY started=$(date -u +%Y-%m-%dT%H:%M:%SZ) node=$(node --version) cucumber-js=$(cucumber-js --version)"
echo "feature files:"
printf '  %s\n' $FEATURES

set +e
# shellcheck disable=SC2086
cucumber-js $FEATURES \
  --require 'tests/behavior/support/**/*.cjs' \
  --require 'tests/behavior/steps/**/*.cjs' \
  --format pretty \
  --format "json:$OUT/behavior-test-report.json"
STATUS=$?
set -e
echo "run.sh: cucumber-js exit $STATUS finished=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
exit "$STATUS"
