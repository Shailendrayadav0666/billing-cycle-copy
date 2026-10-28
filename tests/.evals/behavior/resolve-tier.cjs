// Resolves which feature files a behaviour tier runs (aire-workflow/common/behavior-spec.md Section 6).
// Usage: node tests/.evals/behavior/resolve-tier.cjs <b1|b2|b3> <unit-key>
// Prints the active feature files, one per line, on stdout. Exclusions are named on stderr.
//
// B1: the unit's own spec/behavior/<unit-key>.feature.
// B2: every OTHER feature file in spec/behavior/ whose work unit has been started (Section 6.0):
//     a unit whose resolved Story Tracker status is "Ready for Development" is excluded;
//     a unit with no tracker row stays active.
// B3: B1 + B2 + spec/behavior.feature.
// The Story Tracker is the resolved view: the shared runtime-artifacts/aire-state.md table plus
// every runtime-artifacts/stories/*/state.md row; the later Recorded wins, then the more
// advanced status (aire-workflow/common/parallel-work-state.md Section 4).
const fs = require('node:fs')
const path = require('node:path')

const [tier, key] = process.argv.slice(2)
if (!['b1', 'b2', 'b3'].includes(tier) || !key) {
  console.error('usage: resolve-tier.cjs <b1|b2|b3> <unit-key>')
  process.exit(2)
}

const behaviorDir = path.join('spec', 'behavior')
const own = path.join(behaviorDir, `${key}.feature`)
if (!fs.existsSync(own)) {
  console.error(`resolve-tier: ${own} does not exist`)
  process.exit(2)
}

const statusRank = { 'Ready for Development': 0, 'In Development': 1, 'Ready for Testing': 2 }

function trackerRows(file) {
  if (!fs.existsSync(file)) return []
  const rows = []
  for (const line of fs.readFileSync(file, 'utf8').split(/\r?\n/)) {
    const cells = line.split('|').map((c) => c.trim())
    // | Story | Title | Requires | Tracker ID | Status | PR | Merged | Start | End | Recorded |
    if (cells.length < 12 || !/^[\w.-]+$/.test(cells[1]) || cells[1] === 'Story') continue
    if (!(cells[5] in statusRank)) continue
    rows.push({ id: cells[1], status: cells[5], recorded: cells[10] })
  }
  return rows
}

function resolvedTracker() {
  const sources = [path.join('runtime-artifacts', 'aire-state.md')]
  const fragments = path.join('runtime-artifacts', 'stories')
  if (fs.existsSync(fragments)) {
    for (const unit of fs.readdirSync(fragments)) sources.push(path.join(fragments, unit, 'state.md'))
  }
  const byId = new Map()
  for (const row of sources.flatMap(trackerRows)) {
    const seen = byId.get(row.id)
    const later = !seen || row.recorded > seen.recorded
    const tie = seen && row.recorded === seen.recorded && statusRank[row.status] > statusRank[seen.status]
    if (later || tie) byId.set(row.id, row)
  }
  return byId
}

function unitId(unitKey) {
  return unitKey.replace(/^(story|bug|enhancement)-/, '')
}

const files = []
if (tier === 'b1' || tier === 'b3') files.push(own)

if (tier === 'b2' || tier === 'b3') {
  const tracker = resolvedTracker()
  const others = fs
    .readdirSync(behaviorDir)
    .filter((f) => f.endsWith('.feature') && f !== `${key}.feature`)
    .sort()
  for (const f of others) {
    const row = tracker.get(unitId(path.basename(f, '.feature')))
    if (row && row.status === 'Ready for Development') {
      console.error(`excluded (not started, Ready for Development): ${path.join(behaviorDir, f)}`)
      continue
    }
    files.push(path.join(behaviorDir, f))
  }
}

if (tier === 'b3') files.push(path.join('spec', 'behavior.feature'))

process.stdout.write(files.map((f) => f.split(path.sep).join('/')).join('\n'))
