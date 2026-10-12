---
name: stitch-delta-local
description: >
  For cycles that chose option B at the Helix connect gate (reverse-engineering docs generated
  locally, no Atlas). Runs on the BASE branch AFTER the cycle's [EPIC]/[BUG]/[ENH] PR has merged,
  reads each pending delta from its cycle archive, and performs a full refresh of the local RE doc
  set against the merged code. The doc set lives in one base-only home,
  aire-archives/local-re/spec/plans/, so the next cycle copies it into spec/plans/ and skips reverse
  engineering. It is the only writer of that home and runs one at a time through a
  stitch-delta-local/<name> PR, so parallel cycles never conflict. It never touches spec/, src/,
  tests/ or Atlas.
when_to_use: >
  Trigger when the user says: "stitch-delta-local", "stitch the delta locally", "refresh the local
  RE docs", "stitch local reverse engineering", "post-merge stitch without Atlas".
allowed-tools: Read Grep Glob Bash Write Edit
---

# Stitch Delta Local — Refresh the Locally Generated RE Docs

Load and execute the agent instructions from:

```
aire-workflow/agents/stitch-delta-local-agent.md
```

Read that file completely and follow every step defined in it.

**Key rules**:
- **Use this instead of `/stitch-delta`** when the cycle generated its RE docs locally (option B at
  the start). The user decides by typing it, and the skill never auto-detects. `/stitch-delta` remains
  the path when Atlas holds the deep dive.
- 🔴 **Base branch, after the cycle PR merged.** An archive present on freshly pulled base is a merged
  cycle.
- 🔴 **A wholly current doc set.** Every section of every RE file is decided against the merged tree:
  REFRESH, KEEP (only on positive re-verification) or REMOVE/RESOLVE. Facts are measured, never carried
  forward.
- **Home**: `aire-archives/local-re/spec/plans/`, plus an append-only
  `aire-archives/local-re/stitch-ledger.md`. On the first run it is seeded from the newest archived RE
  set. Several pending deltas means one pass, with one ledger row each.
- 🔴 **Conflict-free by construction.** It is the only writer of the home, one run at a time (it refuses
  while a `stitch-delta-local/*` PR is open). Cycles only copy the home into their own `spec/`, which they
  remove at archive time.
- 🔴 **Never commits to base directly.** It uses a `stitch-delta-local/<name>` branch and a `[STITCH]` PR
  with the `ai-generated` and `aire-v[N]` labels, and an `AIRE-Version: [N]` trailer read live from
  `CLAUDE.md`.
- **Nothing pending is a normal outcome**: report it and stop.
