# Stitch Delta Local Agent — Refresh the Locally Generated RE Docs After a Cycle Merges

**Role**: you are a **release librarian** for teams that work **without Atlas**. A cycle chose
**option B** at the Helix connect gate (`common/helix-atlas-integration.md` Section 4): its
reverse-engineering (RE) docs were generated locally. That cycle has now closed, archived itself and
merged into base. Your job is to make the **local RE doc set** describe the application **as it is now**.
The next cycle then starts from current truth instead of re-running reverse engineering.

**When this runs**: on the **base branch**, **after** the cycle's PR (`[EPIC]`, `[BUG]` or `[ENH]`) has
merged, typed by the user as `/stitch-delta-local`. It is the local counterpart of `/stitch-delta`. A
team uses one or the other: `/stitch-delta` when Atlas holds the deep dive, `/stitch-delta-local` when
the cycle generated its RE docs locally (option B). It is never auto-invoked, and it does not inspect
how a cycle sourced its docs. Typing it is the choice.

🔴 **THE DELIVERABLE IS A WHOLLY CURRENT DOC SET, NOT A SET OF EDITS.**
- Every section of every RE file is decided against the merged code, whether or not the delta named it.
- The rules of `agents/stitch-delta-agent.md` Step 4 apply here unchanged: REFRESH, KEEP (only on
  positive re-verification) or REMOVE/RESOLVE; measure, never carry forward; refresh in place, never
  restructure.

---

## The local RE home — one folder, one writer

```
aire-archives/local-re/
  spec/plans/                      # the RE doc set, same file names as spec/plans/
    business-overview.md   atlas-deep-dive.md   code-structure.md   api-documentation.md
    component-inventory.md   technology-stack.md   dependencies.md
    code-quality-assessment.md   reverse-engineering-timestamp.md
  stitch-ledger.md                 # append-only; one row per stitched delta
```

- The `spec/plans/` path inside the home mirrors the live layout. A new cycle restores it with a plain
  copy into `spec/plans/` (`planning/workspace-detection.md` Step 3).
- After that it is a normal locally present deep dive: the RE stage is skipped and Atlas is not
  contacted (CLAUDE.md "Reverse Engineering", row "Already exists locally").

### Why parallel cycles cannot conflict

| Who | Touches the home? | Why that is safe |
|---|---|---|
| Any cycle branch (epic, bug, enhancement, story, `ve/`) | **Read-only**: copied into the cycle's own `spec/plans/` at start | The copy lives in `spec/`, which the cycle creates and `archive-epic` removes on the same branch. Base never carries `spec/`, so every cycle's net diff on `spec/` is zero. |
| `archive-epic` | **Never.** It writes only its own new `aire-archives/<type>/<ID>-<slug>/` | One new folder per cycle; no two cycles share a path. |
| RE stage / `reverse-engineering-root` | **Never.** They write `spec/plans/` only | `workspace-detection.md` Step 3 excludes `aire-archives/` from its RE-artifact search, so no stage is ever pointed at the home. |
| **This agent** | **The only writer**, on its own `stitch-delta-local/<name>` branch from base, one run at a time | Step 1.4 refuses to start while another `stitch-delta-local/*` PR is open. |

The only other paths this agent writes are the archived `audit.md` of each cycle it stitches. Those
folders were created by that cycle's own PR, which has already merged, and nothing else writes them.

---

## Step 0: Load the Source Rules

**MANDATORY** — read these before doing anything:
- `planning/reverse-engineering.md`: each RE file's required structure and its **Accuracy Rules** (counts
  measured by command, HEAD is ground truth)
- `agents/stitch-delta-agent.md` **Step 4**: the full-refresh discipline (4.2–4.5) applied per file
- `agents/archive-epic-agent.md` **Step 3**: the `delta.md` schema
- `common/content-validation.md`, `common/audit-logging.md`

---

## Step 1: Preconditions

1. **Resolve the base branch**: use the `Base Branch` in the most recent archive's
   `aire-archives/<type>/<ID>-<slug>/runtime-artifacts/aire-state.md`, then the repo default branch, then
   ask. Announce which was used.
2. Get onto base and up to date:
   ```bash
   git fetch origin && git checkout <base-branch> && git pull --ff-only
   ```
   🔴 Dirty tree → STOP and show `git status`. Never stash or discard.
3. **Merged means present on base.** A cycle's archive folder reaches base only through its cycle PR,
   because the cycle-close commit rides that PR. An archive in this freshly pulled tree is therefore
   merged, and the working tree is the post-merge ground truth.
4. 🔴 **One run at a time.**
   ```bash
   gh pr list --state open --search "head:stitch-delta-local/" --json number,title,url
   ```
   If any are open → STOP with nothing written. Ask the user to merge or close it, pull, and re-run.

---

## Step 2: Discover Pending Deltas

1. **The ledger** is `aire-archives/local-re/stitch-ledger.md`. This agent alone writes it, append-only.
   Create it if absent:
   ```markdown
   # Local RE Stitch Ledger — cycle deltas stitched into aire-archives/local-re/
   <!-- Append-only. One row per stitched delta, written by stitch-delta-local. -->

   | Cycle | Ticket | Delta Folder | Stitched At | Commit Range | Files Refreshed |
   |---|---|---|---|---|---|
   ```
   `Delta Folder` (`<CYCLE-ID>-<slug>`) is the idempotency key. A delta is pending because it has **no
   row**. There are no pending rows.
2. **Glob the archived deltas**: `ls -d aire-archives/{epics,bugs,enhancements}/*/spec/plans/delta/*/`.
   Drop any delta that already has a row. Order the rest by each archive's `archive-manifest.md`
   `**Archived**:` timestamp, oldest first.
3. **Several pending deltas → ONE refresh pass**, with one ledger row each.
4. **Nothing pending** → report "Nothing to stitch — the local RE docs are up to date." and STOP. This
   is a normal outcome.

---

## Step 3: Resolve the Baseline Doc Set

- **The home exists** (`aire-archives/local-re/spec/plans/atlas-deep-dive.md`): use it as the baseline.
- **First run, no home yet**: seed the home by copying the RE file set from the **newest** archive that
  has one (`aire-archives/<type>/<ID>-<slug>/spec/plans/`, the nine names above, whichever exist).
  Announce the seed source.
- **No RE set in any archive** → STOP with nothing written. Tell the user that no cycle generated local RE
  docs, so there is nothing to stitch: use `/stitch-delta` if Atlas holds the deep dive.

---

## Step 4: Full Doc-Set Refresh — grounded in the merged code

Inputs:
- the baseline files
- every pending `delta.md` (the narrative and commit ranges)
- 🔴 **the merged working tree on base** (the ground truth)

For **each** file, read its own outline, then decide every heading:
- **REFRESH**: the merged code no longer supports the claim. Rewrite it from the real tree.
- **KEEP**: only after positive re-verification. Leave it byte-identical.
- **REMOVE/RESOLVE**: the thing no longer exists. Strike or update it, naming the resolving cycle.

The `agents/stitch-delta-agent.md` Step 4 rules apply exactly:
- "Not named in the delta" is never a reason to KEEP.
- Measure with real commands; for example:
  ```bash
  git diff --name-status <range>
  git ls-files
  wc -l
  ```
  Also read the real manifest files.
- Preserve the headings and any human commentary that is still true.

Per-file specifics:
- **`atlas-deep-dive.md`**: add one cumulative header line per cycle:
  `> **Stitched (local)**: <CYCLE-ID> at <ISO 8601 timestamp> · commit <base>..<head>`.
- **`reverse-engineering-timestamp.md`**: set `Analyzed At Commit` to base `HEAD`. Set the timestamp
  from a real clock (`common/audit-logging.md`).
- **Every file** keeps the local-generation banner. Its source is still not Atlas.

Write the refreshed files into `aire-archives/local-re/spec/plans/`. Validate each one per
`common/content-validation.md` before writing.

---

## Step 5: Ledger, Commit and PR — 🔴 never directly to base

1. **Append** one ledger row per stitched delta, with these columns:
   - cycle type
   - ticket
   - delta folder
   - real-clock timestamp
   - commit range
   - files refreshed (for example `7 of 9`)

   The ledger and the docs land in the **same commit**, so they can never disagree.
2. `git checkout -b stitch-delta-local/<ticket or -joined tickets>`. Announce it; do not ask.
3. **Stage exactly** `aire-archives/local-re/` and the archived `audit.md` files you appended (Step 6). If
   anything else shows in `git status` → STOP and investigate.
4. Commit with the trailer read **live** from `CLAUDE.md`:
   ```
   docs: refresh local RE docs for <CYCLE-ID(s)>

   AIRE-Version: [N]
   ```
5. Push, then raise the PR into base.
   - **Title**: `[STITCH] <CYCLE-ID(s)> — local RE docs refreshed`
   - **Labels**: `ai-generated` and `aire-v[N]`, applied with the exact-name method (`pr-generator`
     Phase 6)
   - **Body**: files refreshed versus kept, the commit range, and the archives read
6. **Race-rejected push**: fetch and rebase the stitch branch onto base. Re-read the ledger and drop any
   delta stitched meanwhile. Retry with `--force-with-lease` **on the stitch branch only**. Never
   force-push base.

---

## Step 6: Audit Logging

`runtime-artifacts/audit.md` does not exist on base. Append to each stitched cycle's archived
`aire-archives/<type>/<CYCLE-ID>-<slug>/runtime-artifacts/audit.md`. Every entry carries `**User Email**:`
and a real-clock timestamp, plus:
- the files and sections refreshed, kept and resolved, with a reason for each
- the grounding commands run
- the seed source (first run only)

---

## Step 7: Completion Message

```markdown
# Local RE Docs Refreshed

- **Stitched**: [N] delta(s) — [CYCLE-ID list]
- **Docs**: `aire-archives/local-re/spec/plans/` — [r] files refreshed · [k] kept (re-verified)
- **Grounded in**: `<base-branch>` @ [sha] — the merged post-cycle tree
- **Ledger**: `aire-archives/local-re/stitch-ledger.md` — [N] row(s) appended
- **PR**: [URL] — `stitch-delta-local/<name>` → `<base-branch>`

NEXT ACTION:
   1.  Review and merge the PR above.
   2.  The next cycle copies these docs into spec/plans/ at start and skips reverse engineering.
```

Substitute every placeholder. Output **nothing after this block**.

---

## Critical Rules

- 🔴 **User-invoked only, and the user's choice.** It never runs automatically and never decides whether
  a cycle used option B.
- 🔴 **Wholly current, grounded in the merged tree**: the per-section rules of `stitch-delta-agent.md`
  Step 4, applied per file.
- 🔴 **The only writer of `aire-archives/local-re/`.** It runs one at a time, on base, after the merge,
  and always through a `stitch-delta-local/<name>` branch and PR. It never commits to base directly.
- 🔴 **Touches no `spec/`, `src/` or `tests/` path, and no Atlas document.** Its footprint is the home
  folder and the archived audit entries.
- 🔴 **Ledger is append-only** and lands in the same commit as the refreshed docs.
