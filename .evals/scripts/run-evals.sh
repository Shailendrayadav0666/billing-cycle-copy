#!/usr/bin/env bash
# Full eval run for Billing-Cycle: static D1-D7 + unit tests with coverage + behaviour tiers.
# Writes the scorecard: eval.json + eval-summary.md.
#
# Usage: run-evals.sh <base-sha> [evidence-dir]

set -uo pipefail

BASE_SHA="${1:-}"
EVIDENCE_DIR="${2:-.evals/evidence}"
CONFIG=".evals/config.json"

if [ -z "$BASE_SHA" ]; then
  echo "usage: $0 <base-sha> [evidence-dir]" >&2
  exit 2
fi

mkdir -p "$EVIDENCE_DIR"
FAILED=0

thr() { python -c "import json; print(json.load(open('$CONFIG'))['thresholds']['$1'])"; }
COV_MIN=$(thr unitTestCoverageMin)
BEH_MIN=$(thr behaviorScenarioPassRateMin)

: > "$EVIDENCE_DIR/stages.ndjson"
stage() { printf '  %-12s %-6s %s\n' "$1" "$2" "$3"; echo "{\"stage\":\"$1\",\"status\":\"$2\",\"detail\":\"$3\"}" >> "$EVIDENCE_DIR/stages.ndjson"; }

# ------------------------------------------------------- 1. static gate D1-D7
echo "=== stage 1: static gates ==="
bash .evals/scripts/run-static-evals.sh "$BASE_SHA" "$EVIDENCE_DIR/static"
if [ $? -ne 0 ]; then stage static FAIL "one or more of D1-D7 breached threshold"; FAILED=1
else stage static PASS "D1-D7 within thresholds"; fi

# --------------------------------------------- 2. unit tests + coverage
echo "=== stage 2: unit tests + coverage ==="
if [ -d tests/unit ] && command -v python >/dev/null 2>&1; then
  python -m pytest tests/unit \
    --cov=src/backend --cov-report=term --cov-report=json:"$EVIDENCE_DIR/coverage.json" \
    -q > "$EVIDENCE_DIR/unit-tests.txt" 2>&1
  PT=$?
  WHOLE=$(python -c "
import json
try:
    print(round(json.load(open('$EVIDENCE_DIR/coverage.json'))['totals']['percent_covered'],2))
except Exception: print(0.0)")

  # Coverage is judged on the CHANGED surface, per .evals/config.json -> scope: changed-files.
  # Whole-module coverage would charge this work unit for every pre-existing untested line it never
  # touched, which on a repo that started at 0% coverage makes the gate unreachable and therefore
  # useless. Both figures are reported so the pre-existing shortfall stays visible.
  python .evals/scripts/changed-line-coverage.py "$BASE_SHA" "$EVIDENCE_DIR/coverage.json" src/backend     > "$EVIDENCE_DIR/changed-coverage.txt" 2>&1
  COV_RC=$?
  CHANGED_COV=$(grep "changed-line coverage" "$EVIDENCE_DIR/changed-coverage.txt" | awk '{print $NF}')
  cat "$EVIDENCE_DIR/changed-coverage.txt"

  if [ $PT -ne 0 ]; then
    stage unit FAIL "pytest exited $PT - see unit-tests.txt"; FAILED=1
  elif [ $COV_RC -eq 0 ]; then
    stage unit PASS "tests green, changed-surface coverage ${CHANGED_COV} >= unitTestCoverageMin ${COV_MIN}% (whole-module ${WHOLE}%)"
  else
    stage unit FAIL "changed-surface coverage ${CHANGED_COV} < unitTestCoverageMin ${COV_MIN}% (whole-module ${WHOLE}%)"; FAILED=1
  fi
else
  stage unit NA "tests/unit does not exist yet - created by dev-implement"
fi

# ------------------------------------------------- 3. behaviour tiers B1/B2/B3
echo "=== stage 3: behaviour tiers ==="
TIERS="${BEHAVIOR_TIERS:-B1,B2}"
if [ ! -f .evals/behavior/run.sh ]; then
  stage behavior NA ".evals/behavior/run.sh not present"
elif [ ! -d tests/behavior ]; then
  # Nothing has been written yet. Reporting a pass rate here would be a false claim:
  # zero scenarios executed is not 100% passing.
  stage behavior NA "tests/behavior does not exist yet - step definitions are written by dev-implement; 0 scenarios executed"
else
  BEHAVIOR_TIERS="$TIERS" bash .evals/behavior/run.sh > "$EVIDENCE_DIR/behavior.txt" 2>&1
  BH=$?
  if [ $BH -ne 0 ]; then
    stage behavior FAIL "tiers $TIERS below behaviorScenarioPassRateMin ${BEH_MIN}%"; FAILED=1
  elif grep -q "no tests ran\|collected 0 items" "$EVIDENCE_DIR/behavior.txt" 2>/dev/null; then
    stage behavior NA "tiers $TIERS: step definitions present but 0 scenarios collected"
  else
    stage behavior PASS "tiers $TIERS met behaviorScenarioPassRateMin ${BEH_MIN}%"
  fi
fi

# --------------------------------------------------------------- 4. scorecard
python - "$EVIDENCE_DIR" "$FAILED" "$BASE_SHA" <<'PYEOF'
import io, json, os, sys, subprocess
d, failed, base = sys.argv[1], sys.argv[2] != "0", sys.argv[3]

stages = []
p = os.path.join(d, "stages.ndjson")
if os.path.exists(p):
    for line in open(p):
        line = line.strip()
        if line:
            try: stages.append(json.loads(line))
            except Exception: pass

gates = []
gp = os.path.join(d, "static", "results.json")
if os.path.exists(gp):
    try: gates = json.load(open(gp)).get("gates", [])
    except Exception: pass

try:
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
except Exception:
    head = "unknown"

eval_json = {
    "evalFrameworkVersion": "1.0.0",
    "scope": "changed-files",
    "baseSha": base,
    "headSha": head,
    "verdict": "FAIL" if failed else "PASS",
    "stages": stages,
    "gates": gates,
}
with io.open(os.path.join(d, "eval.json"), "w", encoding="utf-8") as fh:
    json.dump(eval_json, fh, indent=2)

lines = ["# Eval Summary", "",
         "**Verdict**: %s" % eval_json["verdict"],
         "**Scope**: changed-files | **Base**: `%s` | **Head**: `%s`" % (base[:12], head[:12]), "",
         "## Stages", "", "| Stage | Status | Detail |", "|---|---|---|"]
for s in stages:
    lines.append("| %s | %s | %s |" % (s.get("stage"), s.get("status"), s.get("detail")))
if gates:
    lines += ["", "## Static gates D1-D7", "", "| Gate | Status | Detail |", "|---|---|---|"]
    for g in gates:
        lines.append("| %s | %s | %s |" % (g.get("gate"), g.get("status"), g.get("detail")))
lines.append("")
io.open(os.path.join(d, "eval-summary.md"), "w", encoding="utf-8").write("\n".join(lines))
print("scorecard -> %s/eval.json and %s/eval-summary.md" % (d, d))
PYEOF

echo "=== eval run: $([ $FAILED -eq 0 ] && echo PASS || echo FAIL) ==="
exit $FAILED
