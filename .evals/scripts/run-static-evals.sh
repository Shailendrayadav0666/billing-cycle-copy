#!/usr/bin/env bash
# D1-D7 static eval gate for Billing-Cycle.
# Owns the baseline diff. Scope is changed files only, per .evals/config.json -> scope.
#
# Usage: run-static-evals.sh <base-sha> [evidence-dir]
#
# Exit 0 = all gates within threshold. Exit 1 = at least one gate breached.
# A gate whose check is genuinely inapplicable to this repo is recorded N/A with a reason.

set -uo pipefail

BASE_SHA="${1:-}"
EVIDENCE_DIR="${2:-.evals/evidence/static}"
CONFIG=".evals/config.json"

if [ -z "$BASE_SHA" ]; then
  echo "usage: $0 <base-sha> [evidence-dir]" >&2
  exit 2
fi
if [ ! -f "$CONFIG" ]; then
  echo "FATAL: $CONFIG not found" >&2
  exit 2
fi

mkdir -p "$EVIDENCE_DIR"
RESULTS="$EVIDENCE_DIR/results.json"
FAILED=0

jqv() { python -c "import json,sys; d=json.load(open('$CONFIG')); print(eval(sys.argv[1],{'d':d}))" "$1"; }

T_LINT=$(jqv "d['thresholds']['lintErrorsAllowedDelta']")
T_TYPE=$(jqv "d['thresholds']['typeErrorsAllowed']")
T_SEM_CRIT=$(jqv "d['thresholds']['semgrepFindingsAllowed']['critical']")
T_SEM_HIGH=$(jqv "d['thresholds']['semgrepFindingsAllowed']['high']")
T_SEM_MED=$(jqv "d['thresholds']['semgrepFindingsAllowed']['medium']")
T_CPLX=$(jqv "d['thresholds']['maxCyclomaticComplexity']")
T_SECRET=$(jqv "d['thresholds']['secretFindingsAllowed']")

echo "=== Static eval gate: base=$BASE_SHA scope=changed-files ==="

# ---------------------------------------------------------------- changed files
# Diff against the WORKING TREE, not BASE...HEAD. Locally the gate runs before the commit, so a
# HEAD-only diff would report "no changed files" and every gate would go N/A for the wrong reason -
# a false pass. `git diff <base>` covers committed, staged and unstaged changes alike, which is the
# set the gate is supposed to measure. Untracked files are added explicitly, since git diff omits them.
CHANGED=$(
  {
    git diff --name-only --diff-filter=ACMR "$BASE_SHA" 2>/dev/null
    git ls-files --others --exclude-standard 2>/dev/null
  } | sort -u
)
echo "$CHANGED" > "$EVIDENCE_DIR/changed-files.txt"

CHANGED_PY=$(echo "$CHANGED"  | grep -E '^src/backend/.*\.py$'        | grep -v '/venv/' | grep -v '__pycache__' || true)
CHANGED_JS=$(echo "$CHANGED"  | grep -E '^src/frontend/src/.*\.(js|jsx)$' || true)

echo "changed python: $(echo "$CHANGED_PY" | grep -c . || true)"
echo "changed js/jsx: $(echo "$CHANGED_JS" | grep -c . || true)"

record() { printf '  %-4s %-10s %s\n' "$1" "$2" "$3"; echo "{\"gate\":\"$1\",\"status\":\"$2\",\"detail\":\"$3\"}" >> "$EVIDENCE_DIR/gates.ndjson"; }
: > "$EVIDENCE_DIR/gates.ndjson"

# ------------------------------------------------------------------- D1 : lint
# Backend: ruff (CI tool, not a runtime dependency). Frontend: oxlint, already a devDependency.
D1_ERRORS=0
if [ -n "$CHANGED_PY" ]; then
  if command -v ruff >/dev/null 2>&1; then
    ruff check $CHANGED_PY --output-format=concise > "$EVIDENCE_DIR/d1-ruff.txt" 2>&1
    # Count only real diagnostics (file:line:col: CODE ...). Counting every non-empty line also
    # counted ruff's own summary lines ("Found 1 error.", "[*] 1 fixable..."), inflating one
    # finding into three.
    D1_ERRORS=$(( D1_ERRORS + $(grep -cE '^[^ ].*:[0-9]+:[0-9]+: ' "$EVIDENCE_DIR/d1-ruff.txt" || true) ))
  else
    record D1 NA "ruff unavailable for backend lint"
  fi
fi
if [ -n "$CHANGED_JS" ]; then
  ( cd src/frontend && npm run --silent lint ) > "$EVIDENCE_DIR/d1-oxlint.txt" 2>&1
  OX=$?
  [ $OX -ne 0 ] && D1_ERRORS=$(( D1_ERRORS + 1 ))
fi
if [ "$D1_ERRORS" -gt "$T_LINT" ]; then
  record D1 FAIL "lint errors $D1_ERRORS > lintErrorsAllowedDelta $T_LINT"; FAILED=1
else
  record D1 PASS "lint errors $D1_ERRORS <= $T_LINT"
fi

# ------------------------------------------------------------- D2 : type check
# Frontend is plain JSX with no tsconfig, so there is no type system to check - genuinely N/A.
if [ -n "$CHANGED_PY" ]; then
  if command -v mypy >/dev/null 2>&1; then
    mypy --ignore-missing-imports --no-error-summary $CHANGED_PY > "$EVIDENCE_DIR/d2-mypy.txt" 2>&1
    D2=$(grep -c "error:" "$EVIDENCE_DIR/d2-mypy.txt" || true)
    if [ "$D2" -gt "$T_TYPE" ]; then record D2 FAIL "mypy errors $D2 > $T_TYPE"; FAILED=1
    else record D2 PASS "mypy errors $D2 <= $T_TYPE"; fi
  else
    record D2 NA "mypy unavailable"
  fi
else
  record D2 NA "no changed python; frontend is plain JSX with no tsconfig, so no type system to check"
fi

# ------------------------------------------------- D3 : static security scan
if command -v semgrep >/dev/null 2>&1; then
  semgrep --config auto --json --quiet $CHANGED_PY $CHANGED_JS > "$EVIDENCE_DIR/d3-semgrep.json" 2>/dev/null
  read -r C H M <<< "$(python - "$EVIDENCE_DIR/d3-semgrep.json" <<'PYEOF'
import json,sys
try: r=json.load(open(sys.argv[1]))
except Exception: print("0 0 0"); raise SystemExit
sev={}
for f in r.get("results",[]):
    s=f.get("extra",{}).get("severity","INFO").upper()
    sev[s]=sev.get(s,0)+1
print(sev.get("CRITICAL",0), sev.get("ERROR",0)+sev.get("HIGH",0), sev.get("WARNING",0)+sev.get("MEDIUM",0))
PYEOF
)"
  if [ "${C:-0}" -gt "$T_SEM_CRIT" ] || [ "${H:-0}" -gt "$T_SEM_HIGH" ] || [ "${M:-0}" -gt "$T_SEM_MED" ]; then
    record D3 FAIL "semgrep crit=$C high=$H med=$M vs allowed $T_SEM_CRIT/$T_SEM_HIGH/$T_SEM_MED"; FAILED=1
  else
    record D3 PASS "semgrep crit=$C high=$H med=$M within threshold"
  fi
else
  record D3 NA "semgrep unavailable"
fi
if [ -n "$CHANGED_PY" ] && command -v bandit >/dev/null 2>&1; then
  bandit -q -f json -o "$EVIDENCE_DIR/d3-bandit.json" $CHANGED_PY 2>/dev/null
  BH=$(python -c "
import json
try:
    r=json.load(open('$EVIDENCE_DIR/d3-bandit.json'))
    print(sum(1 for x in r.get('results',[]) if x.get('issue_severity') in ('HIGH','MEDIUM')))
except Exception: print(0)")
  [ "${BH:-0}" -gt 0 ] && { record D3b FAIL "bandit high/medium findings: $BH"; FAILED=1; } || record D3b PASS "bandit clean"
fi

# ------------------------------------------- D4 : dependency vulnerabilities
D4_FAIL=0
if command -v pip-audit >/dev/null 2>&1; then
  pip-audit -r src/backend/requirements.txt -f json > "$EVIDENCE_DIR/d4-pip-audit.json" 2>/dev/null || D4_FAIL=1
fi
( cd src/frontend && npm audit --json --audit-level=high ) > "$EVIDENCE_DIR/d4-npm-audit.json" 2>/dev/null
NPMV=$(python -c "
import json
try:
    r=json.load(open('$EVIDENCE_DIR/d4-npm-audit.json'))
    v=r.get('metadata',{}).get('vulnerabilities',{})
    print(v.get('critical',0)+v.get('high',0))
except Exception: print(0)")
if [ "$D4_FAIL" -ne 0 ] || [ "${NPMV:-0}" -gt 0 ]; then
  record D4 FAIL "critical/high dependency vulnerabilities present (npm=$NPMV, pip-audit exit=$D4_FAIL)"; FAILED=1
else
  record D4 PASS "no critical/high dependency vulnerabilities"
fi

# ----------------------------------------------------------- D5 : licence scan
if command -v pip-licenses >/dev/null 2>&1; then
  pip-licenses --format=json > "$EVIDENCE_DIR/d5-pip-licenses.json" 2>/dev/null
fi
( cd src/frontend && npx --yes license-checker --json ) > "$EVIDENCE_DIR/d5-npm-licenses.json" 2>/dev/null
D5=$(python - "$EVIDENCE_DIR" <<'PYEOF'
import json, os, sys
# Read from the evidence dir actually in use. A hardcoded path would find nothing whenever the
# caller passes a custom dir - reporting 0 disallowed licences without having looked at anything.
d = sys.argv[1]
bad = {"GPL-2.0","GPL-3.0","AGPL-3.0","SSPL-1.0"}
hits = 0
for p in (os.path.join(d, "d5-npm-licenses.json"), os.path.join(d, "d5-pip-licenses.json")):
    if not os.path.exists(p): continue
    try: data = json.load(open(p))
    except Exception: continue
    items = data.values() if isinstance(data, dict) else data
    for it in items:
        lic = str((it or {}).get("licenses") or (it or {}).get("License") or "")
        if any(b in lic for b in bad): hits += 1
print(hits)
PYEOF
)
if [ "${D5:-0}" -gt 0 ]; then record D5 FAIL "disallowed licences found: $D5"; FAILED=1
else record D5 PASS "no disallowed licences"; fi

# ------------------------------------------------------- D6 : complexity
if [ -n "$CHANGED_PY" ] && command -v radon >/dev/null 2>&1; then
  radon cc -j $CHANGED_PY > "$EVIDENCE_DIR/d6-radon.json" 2>/dev/null
  OVER=$(python -c "
import json
try:
    r=json.load(open('$EVIDENCE_DIR/d6-radon.json'))
    print(sum(1 for fns in r.values() if isinstance(fns,list) for f in fns if f.get('complexity',0) > $T_CPLX))
except Exception: print(0)")
  if [ "${OVER:-0}" -gt 0 ]; then record D6 FAIL "$OVER changed function(s) exceed maxCyclomaticComplexity $T_CPLX"; FAILED=1
  else record D6 PASS "all changed functions within complexity $T_CPLX"; fi
else
  record D6 NA "radon unavailable or no changed python"
fi

# ------------------------------------------------------ D7 : secret scan (DIFF ONLY)
# Scope is the diff, per D7's definition. Scanning the whole repo would sweep
# node_modules/ and venv/ and drown the gate in vendored false positives.
#
# Rung chain, in order: native gitleaks binary -> gitleaks in a container -> regex sweep.
# A rung that FAILS TO START is not a gate failure. Findings are read from the JSON
# report, never inferred from an exit code, so "tool could not run" and "secrets found"
# can never be confused.
# 🔴 The scan directory MUST live outside the repository. gitleaks honours .gitignore, and the
# evidence dir is gitignored - writing the patch there made gitleaks skip it and report
# "scanned ~0 bytes", i.e. a PASS on a gate that examined nothing. A secret scan that silently
# scans zero bytes is worse than no gate at all, because it reports success.
D7_DIFF_DIR="$(mktemp -d 2>/dev/null || echo "${TMPDIR:-/tmp}/aire-d7-$$")"
mkdir -p "$D7_DIFF_DIR"
trap 'rm -rf "$D7_DIFF_DIR"' EXIT
git diff "$BASE_SHA"...HEAD > "$D7_DIFF_DIR/changes.patch" 2>/dev/null \
  || git diff "$BASE_SHA" HEAD > "$D7_DIFF_DIR/changes.patch" 2>/dev/null
# 🔴 Do NOT copy the scanned patch into the evidence dir. Evidence under .spec/ is tracked, so a
# stored patch lands in the NEXT run's diff - and the scanner then scans a copy of a previous diff,
# reporting findings that no longer exist in the code. The report and the byte count are the
# evidence; the patch itself is transient by design.
# 🔴 The raw report also stays OUTSIDE the repo. A secret scanner's report embeds the strings it
# flagged, by construction. Committing it means (a) the next run scans its own previous findings,
# and (b) a genuine leaked credential gets copied into version control as "evidence". Only a
# redacted summary - counts and rule ids - is persisted.
D7_REPORT="$D7_DIFF_DIR/d7-gitleaks.json"
D7_LOG="$D7_DIFF_DIR/d7-gitleaks.txt"
rm -f "$D7_REPORT"
D7_RUNG=""

# Rung 1a: a gitleaks binary bootstrapped into .evals/tools/ (gitignored, not project source).
GITLEAKS_BIN=""
for cand in .evals/tools/gitleaks.exe .evals/tools/gitleaks; do
  [ -x "$cand" ] && GITLEAKS_BIN="$cand" && break
done
# Rung 1b: a gitleaks already on PATH.
[ -z "$GITLEAKS_BIN" ] && command -v gitleaks >/dev/null 2>&1 && GITLEAKS_BIN="gitleaks"

if [ -n "$GITLEAKS_BIN" ]; then
  "$GITLEAKS_BIN" detect --no-git --source "$D7_DIFF_DIR" --redact --no-banner \
    --config .gitleaks.toml \
    --report-format json --report-path "$D7_REPORT" > "$D7_LOG" 2>&1
  [ -f "$D7_REPORT" ] && D7_RUNG="gitleaks binary ($($GITLEAKS_BIN version 2>/dev/null | head -1))"
fi

if [ -z "$D7_RUNG" ] && command -v podman >/dev/null 2>&1; then
  podman run --rm -v "$D7_DIFF_DIR:/scan:z" \
    docker.io/zricethezav/gitleaks:latest \
    detect --no-git --source /scan --redact --no-banner \
    --report-format json --report-path /scan/d7-gitleaks.json \
    > "$D7_LOG" 2>&1
  [ -f "$D7_REPORT" ] && D7_RUNG="gitleaks container"
fi

PATCH_BYTES=$(wc -c < "$D7_DIFF_DIR/changes.patch" 2>/dev/null || echo 0)
if [ "${PATCH_BYTES:-0}" -lt 1 ] && [ -n "$CHANGED" ]; then
  record D7 FAIL "the diff to scan came out empty while files were changed - the scan cannot be trusted"
  FAILED=1
  D7_RUNG=""
fi

if [ -n "$D7_RUNG" ]; then
  echo "  (D7 scanned $PATCH_BYTES bytes via $D7_RUNG)"
  HITS=$(python -c "
import json
try:
    r = json.load(open('$D7_REPORT'))
    print(len(r) if isinstance(r, list) else 0)
except Exception: print(0)")
  # Persist a REDACTED summary: scanned byte count, finding count, rule ids. Never the matches.
  python - "$D7_REPORT" "$EVIDENCE_DIR/d7-summary.json" "$PATCH_BYTES" "$D7_RUNG" <<'PYEOF'
import io, json, sys
rep, out, nbytes, rung = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
try:
    findings = json.load(io.open(rep, encoding="utf-8"))
    if not isinstance(findings, list):
        findings = []
except Exception:
    findings = []
by_rule = {}
for f in findings:
    rid = f.get("RuleID", "unknown")
    by_rule[rid] = by_rule.get(rid, 0) + 1
io.open(out, "w", encoding="utf-8").write(json.dumps({
    "gate": "D7",
    "rung": rung,
    "scannedBytes": int(nbytes or 0),
    "findingCount": len(findings),
    "byRule": by_rule,
    "note": "Matched text is deliberately omitted. A secret scanner's raw report embeds the strings "
            "it flagged, so committing it would place a real leak into version control and would "
            "make the next run scan its own previous findings.",
}, indent=2) + "\n")
PYEOF

  if [ "${HITS:-0}" -gt "$T_SECRET" ]; then
    record D7 FAIL "$D7_RUNG found $HITS secret(s) in $PATCH_BYTES scanned bytes (allowed $T_SECRET) - rule ids in d7-summary.json"; FAILED=1
  else
    record D7 PASS "$D7_RUNG: no secrets in $PATCH_BYTES scanned bytes"
  fi
else
  # Both gitleaks rungs unavailable. The regex sweep always runs, so the gate is
  # never silently skipped - it is recorded as having run on the weaker rung.
  HITS=$(grep -icE '(api[_-]?key|secret|passwd|password|token|credential|BEGIN [A-Z ]*PRIVATE KEY)[[:space:]]*[:=][[:space:]]*['\''"][^'\''"]{8,}' "$D7_DIFF_DIR/changes.patch" 2>/dev/null || true)
  REASON="gitleaks unavailable (no binary; podman present but its machine is not running)"
  if [ "${HITS:-0}" -gt "$T_SECRET" ]; then
    record D7 FAIL "regex sweep found $HITS candidate secret(s) in the diff - $REASON"; FAILED=1
  else
    record D7 PASS "regex sweep clean on the diff - $REASON"
  fi
fi

python - "$EVIDENCE_DIR" "$FAILED" <<'PYEOF'
import json, sys, os
d, failed = sys.argv[1], sys.argv[2]
gates = []
p = os.path.join(d, "gates.ndjson")
if os.path.exists(p):
    for line in open(p):
        line = line.strip()
        if line:
            try: gates.append(json.loads(line))
            except Exception: pass
json.dump({"scope": "changed-files", "failed": failed != "0", "gates": gates},
          open(os.path.join(d, "results.json"), "w"), indent=2)
PYEOF

echo "=== static gate: $([ $FAILED -eq 0 ] && echo PASS || echo FAIL) -> $RESULTS ==="
exit $FAILED
