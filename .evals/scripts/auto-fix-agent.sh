#!/usr/bin/env bash
# CI self-repair: runs the Claude Code CLI to fix failing gates, capped at
# retryLimitForSelfRepair from .evals/config.json.
#
# Authentication: CLAUDE_CODE_OAUTH_TOKEN (from `claude setup-token`) or ANTHROPIC_API_KEY.
# Without either, this script exits 0 without doing anything - the gates still ran and
# still blocked the PR. Self-repair is an accelerator, never the enforcement.
#
# Usage: auto-fix-agent.sh <base-sha> [evidence-dir]

set -uo pipefail

BASE_SHA="${1:-}"
EVIDENCE_DIR="${2:-.evals/evidence}"
CONFIG=".evals/config.json"

if [ -z "$BASE_SHA" ]; then
  echo "usage: $0 <base-sha> [evidence-dir]" >&2
  exit 2
fi

if [ -z "${CLAUDE_CODE_OAUTH_TOKEN:-}" ] && [ -z "${ANTHROPIC_API_KEY:-}" ]; then
  echo "No CLAUDE_CODE_OAUTH_TOKEN or ANTHROPIC_API_KEY configured."
  echo "Skipping self-repair. The gate results stand and continue to block the PR."
  exit 0
fi

LIMIT=$(python -c "import json; print(json.load(open('$CONFIG'))['retryLimitForSelfRepair'])")
echo "Self-repair budget: $LIMIT attempt(s)"

if ! command -v claude >/dev/null 2>&1; then
  echo "Installing Claude Code CLI..."
  npm install -g @anthropic-ai/claude-code || { echo "install failed; skipping self-repair"; exit 0; }
fi

SUMMARY="$EVIDENCE_DIR/eval-summary.md"
[ -f "$SUMMARY" ] || { echo "no $SUMMARY to work from; skipping"; exit 0; }

ATTEMPT=1
while [ "$ATTEMPT" -le "$LIMIT" ]; do
  echo "=== self-repair attempt $ATTEMPT of $LIMIT ==="

  claude -p "$(cat <<PROMPT
The CI eval gate for this repository is failing. Fix the underlying causes.

Failing gate report:
$(cat "$SUMMARY")

Hard rules you must not break:
1. Do NOT modify .evals/config.json. Lowering a threshold to pass a gate is forbidden.
2. Do NOT modify or delete any test to make it pass. Fix the code the test is exercising.
3. Do NOT add a runtime dependency to src/backend/requirements.txt or src/frontend/package.json.
   Constraint ARCH-05 in .spec/architecture.md forbids it.
4. Respect every constraint in .spec/architecture.md Section 10 (ARCH-01..ARCH-06).
   In particular: no state write may precede the charge_card call, no request model may
   accept an amount, and no store lookup may take a fallback record.
5. Change only what the failing gates require. Do not refactor anything else.

Read .spec/architecture.md and .spec/aire-docs/implementation/design/ before editing.
PROMPT
)" --permission-mode acceptEdits --allowed-tools "Read,Edit,Write,Bash,Grep,Glob" \
    > "$EVIDENCE_DIR/self-repair-$ATTEMPT.log" 2>&1

  echo "Re-running the gate..."
  if bash .evals/scripts/run-evals.sh "$BASE_SHA" "$EVIDENCE_DIR"; then
    echo "=== gates green after attempt $ATTEMPT ==="
    if [ -n "$(git status --porcelain)" ]; then
      git config user.name  "aire-ci[bot]"
      git config user.email "aire-ci[bot]@users.noreply.github.com"
      git add -A
      git commit -m "fix(ci): self-repair failing eval gates (attempt $ATTEMPT)

Automated repair by the Claude Code CLI. Thresholds unchanged; no test weakened.

AIRE-Version: 1.0"
      git push
    fi
    exit 0
  fi

  ATTEMPT=$(( ATTEMPT + 1 ))
done

echo "=== RETRY LIMIT REPORT ==="
echo "Self-repair exhausted $LIMIT attempt(s) and the gate is still failing."
echo "The gate has NOT been skipped, weakened, or carried forward. Human attention required."
echo "Latest report:"
cat "$SUMMARY"
exit 1
