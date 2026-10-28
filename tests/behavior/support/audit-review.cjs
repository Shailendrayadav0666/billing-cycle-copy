// Reviews an `npm audit --json` result the way the D4 gate does: a high or critical advisory that
// reaches a newly added dependency blocks the story, up to the limits in tests/.evals/config.json
// (thresholds.dependencyVulnerabilitiesAllowed).
const fs = require('node:fs')
const path = require('node:path')

const REPO = path.resolve(__dirname, '../../..')

function allowedVulnerabilities() {
  const config = JSON.parse(fs.readFileSync(path.join(REPO, 'tests/.evals/config.json'), 'utf8'))
  return config.thresholds.dependencyVulnerabilitiesAllowed
}

// Every package an advisory reaches: the vulnerable package itself plus, through npm's
// `effects` graph, every package that depends on it.
function reachedPackages(vulnerabilities, name) {
  const reached = new Set([name])
  const queue = [name]
  while (queue.length > 0) {
    const entry = vulnerabilities[queue.shift()]
    for (const parent of (entry && entry.effects) || []) {
      if (!reached.has(parent)) {
        reached.add(parent)
        queue.push(parent)
      }
    }
  }
  return reached
}

function reviewAudit(audit, newDependencies, allowed = allowedVulnerabilities()) {
  const vulnerabilities = audit.vulnerabilities || {}
  const counts = { high: 0, critical: 0 }
  const blocking = []
  for (const [name, entry] of Object.entries(vulnerabilities)) {
    if (!(entry.severity in counts)) continue
    const reached = reachedPackages(vulnerabilities, name)
    const nested = (entry.nodes || []).some((node) =>
      newDependencies.some((dep) => node.startsWith(`node_modules/${dep}/`)),
    )
    if (nested || newDependencies.some((dep) => reached.has(dep))) {
      counts[entry.severity] += 1
      blocking.push({ name, severity: entry.severity })
    }
  }
  const complete = Object.keys(counts).every((severity) => counts[severity] <= allowed[severity])
  return { complete, counts, blocking }
}

module.exports = { reviewAudit, allowedVulnerabilities }
