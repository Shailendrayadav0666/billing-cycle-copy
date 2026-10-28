// Step definitions for spec/behavior/story-1.1.feature (Frontend unit-test tooling).
// They bind to the project's public surface only: package.json, the npm scripts, the lock file,
// git's ignore and index state, the story's saved evidence, and the D4 threshold in
// tests/.evals/config.json.
const assert = require('node:assert/strict')
const fs = require('node:fs')
const os = require('node:os')
const path = require('node:path')
const { spawnSync } = require('node:child_process')
const { Given, When, Then, setDefaultTimeout } = require('@cucumber/cucumber')
const { reviewAudit } = require('../support/audit-review.cjs')

setDefaultTimeout(240 * 1000)

const REPO = path.resolve(__dirname, '../../..')
// The test libraries Story 1.1 adds (spec/plans/stories.md AC-1, plus their required companions).
const NEW_DEV_DEPENDENCIES = [
  'vitest',
  '@vitest/coverage-v8',
  'jsdom',
  '@testing-library/react',
  '@testing-library/dom',
]

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, 'utf8'))
}

function git(args) {
  return spawnSync('git', args, { cwd: REPO, encoding: 'utf8' })
}

function passedTestTitles(report) {
  return report.testResults
    .flatMap((file) => file.assertionResults)
    .filter((test) => test.status === 'passed')
    .map((test) => test.title)
}

Given('the frontend project in {string} with its package.json', function (dir) {
  this.projectDir = path.join(REPO, dir)
  assert.ok(fs.existsSync(path.join(this.projectDir, 'package.json')), `${dir}/package.json is missing`)
})

// AC-1 ---------------------------------------------------------------------------------------

When("the project's dependency manifest is inspected", function () {
  this.manifest = readJson(path.join(this.projectDir, 'package.json'))
})

Then('{string}, {string} and {string} are listed under devDependencies', function (a, b, c) {
  this.testLibraries = [a, b, c]
  const dev = this.manifest.devDependencies || {}
  for (const name of this.testLibraries) {
    assert.ok(name in dev, `${name} is not listed under devDependencies`)
  }
})

Then('none of them is listed under dependencies', function () {
  const deps = this.manifest.dependencies || {}
  for (const name of this.testLibraries) {
    assert.ok(!(name in deps), `${name} is listed under dependencies`)
  }
})

Then('the dependencies section still lists only {string}, {string} and {string}', function (a, b, c) {
  assert.deepEqual(Object.keys(this.manifest.dependencies || {}).sort(), [a, b, c].sort())
})

// AC-2 and AC-3 ------------------------------------------------------------------------------

Given('the {string} response is mocked with plan_name {string} and price {string}', function (endpoint, plan, price) {
  this.mock = { endpoint, plan, price }
})

When('a developer runs {string} in {string}', function (command, dir) {
  const [tool, sub, script] = command.split(' ')
  assert.equal(`${tool} ${sub}`, 'npm run', `unsupported command: ${command}`)
  const cwd = path.join(REPO, dir)
  const args = ['run', script]
  if (script === 'test') {
    // Same npm script; the extra reporters only add a machine-readable copy of the results.
    this.reportFile = path.join(fs.mkdtempSync(path.join(os.tmpdir(), 'vitest-')), 'report.json')
    args.push('--', '--reporter=default', '--reporter=json', `--outputFile.json=${this.reportFile}`)
  }
  if (script === 'test:coverage') {
    fs.rmSync(path.join(cwd, 'coverage'), { recursive: true, force: true })
  }
  this.startedAt = Date.now()
  this.run = spawnSync('npm', args, { cwd, encoding: 'utf8' })
  this.output = `${this.run.stdout}\n${this.run.stderr}`
  if (this.reportFile && fs.existsSync(this.reportFile)) this.report = readJson(this.reportFile)
})

Then('the tests run in a jsdom environment', function () {
  assert.ok(this.report, `no Vitest report was written\n${this.output}`)
  assert.ok(passedTestTitles(this.report).includes('runs in the jsdom environment'))
})

Then('a smoke test renders the Billing page and finds the {string} heading', function (heading) {
  const { endpoint, plan, price } = this.mock
  const smoke = passedTestTitles(this.report).find(
    (title) =>
      title.includes('renders the Billing page') &&
      title.includes(`mocked ${endpoint} response`) &&
      title.includes(`plan_name "${plan}"`) &&
      title.includes(`price "${price}"`) &&
      title.includes(`"${heading}" heading`),
  )
  assert.ok(smoke, `no passing smoke test renders the Billing page and finds "${heading}"`)
})

Then('the command exits with status {int}', function (status) {
  assert.equal(this.run.status, status, this.output)
  assert.ok(this.report.numTotalTests > 0, 'no tests ran')
  assert.equal(this.report.numFailedTests, 0)
})

Then('no request reaches a real {string} endpoint', function (endpoint) {
  assert.ok(
    passedTestTitles(this.report).includes(`uses only the mocked ${endpoint} response and never calls the real endpoint`),
    `no passing test proves ${endpoint} is mocked`,
  )
})

Then('a text coverage summary is printed', function () {
  assert.equal(this.run.status, 0, this.output)
  assert.match(this.run.stdout, /% Stmts/)
  assert.match(this.run.stdout, /All files/)
})

Then('an lcov report is written to {string}', function (file) {
  const lcov = path.join(REPO, file)
  assert.ok(fs.existsSync(lcov), `${file} was not written`)
  assert.ok(fs.statSync(lcov).mtimeMs >= this.startedAt - 1000, `${file} is older than this run`)
  const content = fs.readFileSync(lcov, 'utf8')
  assert.match(content, /^SF:/m)
  assert.match(content, /^end_of_record$/m)
})

// AC-4 ---------------------------------------------------------------------------------------

When("the story's changes are committed", function () {
  const inside = git(['rev-parse', '--is-inside-work-tree'])
  assert.equal(inside.stdout.trim(), 'true', `git cannot read the repository: ${inside.stderr}`)
})

Then('{string} is part of the commit and records the exact resolved versions of the new dev dependencies', function (file) {
  const tracked = git(['ls-files', '--error-unmatch', file])
  assert.equal(tracked.status, 0, `${file} is not in the git index (staged or committed)`)
  const lock = readJson(path.join(REPO, file))
  const manifest = readJson(path.join(REPO, path.dirname(file), 'package.json'))
  for (const name of NEW_DEV_DEPENDENCIES) {
    const entry = lock.packages[`node_modules/${name}`]
    assert.ok(entry, `${name} is not in ${file}`)
    assert.match(entry.version, /^\d+\.\d+\.\d+$/, `${name} has no exact version`)
    assert.ok(entry.resolved.startsWith('https://registry.npmjs.org/'), `${name} is not from the npm registry`)
    assert.match(entry.integrity, /^sha512-/, `${name} has no integrity hash`)
    assert.equal(entry.dev, true, `${name} is not a dev-only package`)
    assert.equal(lock.packages[''].devDependencies[name], manifest.devDependencies[name])
  }
})

Then('{string} is no longer ignored by {string}', function (file, ignoreFile) {
  const ignored = git(['check-ignore', '--no-index', '-v', file])
  assert.equal(ignored.status, 1, `${file} is still ignored: ${ignored.stdout}`)
  const rules = fs.readFileSync(path.join(REPO, ignoreFile), 'utf8').split(/\r?\n/).map((l) => l.trim())
  assert.ok(!rules.includes(path.basename(file)), `${ignoreFile} still lists ${path.basename(file)}`)
})

Then("the {string} result is saved in the story's evidence", function (tool) {
  assert.equal(tool, 'npm audit')
  const key = process.env.AIRE_STORY_KEY
  const dir = path.join(REPO, 'reports', 'eval-evidence', key)
  const saved = fs.existsSync(dir) ? fs.readdirSync(dir).filter((f) => /^npm-audit.*\.json$/.test(f)) : []
  assert.ok(saved.length > 0, `no npm audit result under reports/eval-evidence/${key}/`)
  for (const f of saved) {
    const audit = readJson(path.join(dir, f))
    assert.ok(audit.metadata && audit.metadata.vulnerabilities, `${f} is not an npm audit result`)
  }
  this.savedAudits = saved.map((f) => readJson(path.join(dir, f)))
})

Given('{string} reports a high or critical advisory for a newly added dev dependency', function (tool) {
  assert.equal(tool, 'npm audit')
  this.audit = {
    auditReportVersion: 2,
    vulnerabilities: {
      vitest: {
        name: 'vitest',
        severity: 'high',
        isDirect: true,
        via: [{ name: 'vitest', title: 'Example advisory for this scenario', severity: 'high', range: '<=5.0.5' }],
        effects: [],
        range: '<=5.0.5',
        nodes: ['node_modules/vitest'],
        fixAvailable: true,
      },
    },
    metadata: { vulnerabilities: { info: 0, low: 0, moderate: 0, high: 1, critical: 0, total: 1 } },
  }
})

When("the story's evidence is reviewed", function () {
  this.review = reviewAudit(this.audit, NEW_DEV_DEPENDENCIES)
  const resolved = { ...this.audit, vulnerabilities: {} }
  this.resolvedReview = reviewAudit(resolved, NEW_DEV_DEPENDENCIES)
  const key = process.env.AIRE_STORY_KEY
  const dir = path.join(REPO, 'reports', 'eval-evidence', key)
  this.actualReviews = fs
    .readdirSync(dir)
    .filter((f) => /^npm-audit.*\.json$/.test(f))
    .map((f) => ({ file: f, review: reviewAudit(readJson(path.join(dir, f)), NEW_DEV_DEPENDENCIES) }))
})

Then('the story is not complete until the advisory is resolved by a non-vulnerable version', function () {
  assert.equal(this.review.complete, false, 'a high advisory on a new dev dependency was accepted')
  assert.deepEqual(this.review.blocking, [{ name: 'vitest', severity: 'high' }])
  assert.equal(this.resolvedReview.complete, true, 'the review still blocks after the advisory is gone')
  assert.ok(this.actualReviews.length > 0, "no npm audit result in the story's evidence")
  for (const { file, review } of this.actualReviews) {
    assert.equal(review.complete, true, `${file} has a blocking advisory: ${JSON.stringify(review.blocking)}`)
  }
})
