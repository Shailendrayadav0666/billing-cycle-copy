// Step definitions for spec/behavior/story-1.1.feature and spec/behavior.feature.
// Bound to the SPA's public surface: the real <App /> (router, AuthProvider, Login, Billing)
// rendered in jsdom, driven the way a user drives it, observed through the rendered DOM.
import { spawnSync } from 'node:child_process'
import { mkdtempSync, readFileSync } from 'node:fs'
import os from 'node:os'
import path from 'node:path'
import { cleanup, render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { After, Before, Given, Then, When } from 'quickpickle'
import { expect, vi } from 'vitest'
import App from '../../../src/frontend/src/App.jsx'
import { FakeBackend, realBackendFetch } from '../support/backend.js'

const repoRoot = path.resolve(import.meta.dirname, '../../..')
const frontendRoot = path.join(repoRoot, 'src/frontend')
const UPGRADE = 'Upgrade to Premium'
globalThis.__aireNativeFetch ??= globalThis.fetch

const baseBilling = () => ({
  plan_name: 'Standard',
  price: '$20/month',
  renew_at: 'Oct 30, 2026',
  usages: [],
  included_usage: { title: 'Plan perks', items: [], help: 'Perks included in your Standard plan.' },
})

function mountApp(world, route) {
  window.history.pushState({}, '', route)
  world.view = render(<App />)
}

async function waitForBilling() {
  await screen.findByText('Plan & Billing', {}, { timeout: 5000 })
}

const button = (name) => screen.queryByRole('button', { name })
const priceText = () => document.querySelector('.plan-price')?.textContent
const badgeText = () => document.querySelector('.current-label .standard-badge')?.textContent

function perkLabels() {
  return [...document.querySelectorAll('.extra-row-header span:first-child')].map((n) => n.textContent)
}

function usageCards() {
  return [...document.querySelectorAll('.usage-card')].map((card) => ({
    label: card.querySelector('.usage-label').textContent,
    value: card.querySelector('.usage-value').textContent,
  }))
}

Before(async (world) => {
  world.requests = []
  world.backend = new FakeBackend()
  world.backend.requests = world.requests
  world.backend.setBilling('tpg@example.com', baseBilling())
  vi.stubGlobal('fetch', (input, init) => world.backend.fetch(input, init))
  localStorage.clear()
})

After(() => {
  cleanup()
  vi.unstubAllGlobals()
  localStorage.clear()
})

// ---------------------------------------------------------------- work-unit Background (fake backend)

Given('the user is logged in', (world) => {
  localStorage.setItem('token', 'tpg@example.com')
  world.loggedInAs = 'tpg@example.com'
})

Given('the billing service returns this plan for the user:', (world, table) => {
  const [row] = table.hashes()
  world.backend.setBilling('tpg@example.com', { ...baseBilling(), ...row })
})

Given('the Standard usage cards are {string}, {string} and {string}', (world, video, screens, downloads) => {
  const b = world.backend.billing['tpg@example.com']
  b.usages = [
    { id: 'video-quality', label: 'Video quality', type: 'feature', value: video, help: 'Video quality help' },
    { id: 'screens', label: 'Watch at the same time', type: 'feature', value: screens, help: 'Screens help' },
    { id: 'downloads', label: 'Download on devices', type: 'feature', value: downloads, help: 'Downloads help' },
  ]
})

Given('the Standard plan perks are {string} and {string}', (world, a, b) => {
  world.backend.billing['tpg@example.com'].included_usage.items = [
    { id: 'ad-free', label: a, used_percent: 100 },
    { id: 'spatial-audio', label: b, used_percent: 100 },
  ]
})

Given('the billing service returns plan_name {string} for the user', (world, plan) => {
  world.backend.billing['tpg@example.com'].plan_name = plan
})

Given('the billing service has not responded yet', (world) => {
  world.backend.pending = true
})

// ---------------------------------------------------------------- page actions

When('the Billing page finishes loading', async (world) => {
  mountApp(world, '/billing')
  await waitForBilling()
  world.loadedRequestCount = world.requests.length
  world.titleNode = screen.getByText('Plan & Billing')
})

When('the Billing page is opened', (world) => {
  mountApp(world, '/billing')
})

When('the user clicks {string}', async (world, name) => {
  world.titleNode = screen.getByText('Plan & Billing')
  await userEvent.click(screen.getByRole('button', { name }))
})

When(/^the (?:Billing page is reloaded|user reloads the Billing page)$/, async (world) => {
  world.view.unmount()
  mountApp(world, '/billing')
  await waitForBilling()
})

When('the user moves focus to the {string} button with the Tab key', async (world, name) => {
  world.user = userEvent.setup()
  const target = screen.getByRole('button', { name })
  for (let i = 0; i < 20 && document.activeElement !== target; i += 1) await world.user.tab()
  expect(target).toHaveFocus()
})

When('the user presses Enter', async (world) => {
  await world.user.keyboard('{Enter}')
})

// ---------------------------------------------------------------- outcomes

Then(/^an? "([^"]+)" button is shown$/, (world, name) => {
  expect(button(name)).toBeInTheDocument()
})

Then(/^(?:the )?"([^"]+)" button is visible$/, (world, name) => {
  expect(button(name)).toBeInTheDocument()
})

Then('no {string} button is shown', (world, name) => {
  expect(button(name)).not.toBeInTheDocument()
})

Then('the button appears after the {string} card and before the {string} heading', (world, card, heading) => {
  const btn = button(UPGRADE)
  const before = btn.previousElementSibling
  expect(before).toHaveClass('plan-row')
  expect(within(before).getByText(card)).toBeInTheDocument()
  expect(btn.nextElementSibling).toHaveClass('section-title')
  expect(btn.nextElementSibling).toHaveTextContent(heading)
})

Then('the button is only as wide as its label and is left-aligned', () => {
  const style = getComputedStyle(button(UPGRADE))
  expect(style.width).toBe('auto')
  expect(style.marginLeft).toBe('0px')
  expect(style.marginRight).toBe('0px')
})

Then('{string} is shown', (world, text) => {
  expect(screen.getByText(text)).toBeInTheDocument()
})

Then('the current plan badge reads {string}', (world, plan) => {
  expect(badgeText()).toBe(plan)
})

Then('the section heading reads {string}', (world, heading) => {
  expect(document.querySelector('.section-title')).toHaveTextContent(heading)
})

Then('the heading reads {string}', (world, heading) => {
  expect(screen.getByRole('heading', { level: 2 })).toHaveTextContent(heading)
})

Then('the badge keeps the existing teal plan-badge styling', () => {
  const badge = document.querySelector('.current-label .standard-badge')
  expect(badge).toBeInTheDocument()
  expect(getComputedStyle(badge).color).toBe('rgb(15, 118, 110)')
})

Then('the page is not reloaded', (world) => {
  expect(screen.getByText('Plan & Billing')).toBe(world.titleNode)
  expect(screen.queryByText('Loading billing...')).not.toBeInTheDocument()
})

Then('the plan price reads {string}', async (world, price) => {
  await waitFor(() => expect(priceText()).toBe(price))
})

Then('the usage cards read:', (world, table) => {
  expect(usageCards()).toEqual(table.hashes())
})

Then('the plan perks are {string}, {string} and {string}', (world, a, b, c) => {
  expect(perkLabels()).toEqual([a, b, c])
})

Then('the plan perks are {string} and {string}', (world, a, b) => {
  expect(perkLabels()).toEqual([a, b])
})

Then(/^the "Renew at" date (?:still )?reads "([^"]+)"$/, (world, date) => {
  expect(document.querySelector('.renew-date')).toHaveTextContent(date)
})

Then('the message {string} is shown', async (world, text) => {
  expect(await screen.findByText(text)).toBeInTheDocument()
})

Then('the message {string} is not shown', (world, text) => {
  expect(screen.queryByText(text)).not.toBeInTheDocument()
})

Then('exactly {int} request to {string} has been made', (world, count, apiPath) => {
  expect(world.requests.filter((r) => r.path === apiPath)).toHaveLength(count)
  world.requestCountAtCheck = world.requests.length
})

Then('still exactly {int} request has been made in total', (world, count) => {
  expect(world.requests.filter((r) => r.path.startsWith('/api/billing'))).toHaveLength(count)
  expect(world.requests.length).toBe(world.requestCountAtCheck)
})

Then('the button shows a visible focus outline', () => {
  const rules = [...document.styleSheets].flatMap((sheet) => [...sheet.cssRules])
  const focusRule = rules.find((r) => r.selectorText === '.upgrade-btn:focus-visible')
  expect(focusRule, 'a .upgrade-btn:focus-visible rule is shipped').toBeDefined()
  expect(focusRule.style.outlineStyle || focusRule.style.outline).toMatch(/solid/)
  expect(button(UPGRADE)).toHaveFocus()
})

Then('the message {string} is in a status region announced politely to assistive technology', async (world, text) => {
  const region = await screen.findByRole('status')
  expect(region).toHaveTextContent(text)
  expect(region.getAttribute('aria-live') ?? 'polite').toBe('polite')
})

// ---------------------------------------------------------------- AC-10: the unit-test suite itself

Given('the frontend dependencies are installed from the committed lock file', () => {
  const lock = JSON.parse(readFileSync(path.join(frontendRoot, 'package-lock.json'), 'utf8'))
  expect(lock.packages['node_modules/vitest']?.version).toBe('5.0.5')
})

When('the developer runs {string} in {string}', (world, command, dir) => {
  const [bin, ...args] = command.split(' ')
  world.coverageDir = mkdtempSync(path.join(os.tmpdir(), 'aire-ac10-'))
  const extra = ['--reporter=verbose', '--coverage', `--coverage.reportsDirectory=${world.coverageDir}`]
  world.run = spawnSync(bin, [...args, '--', ...extra], {
    cwd: path.join(repoRoot, dir),
    encoding: 'utf8',
    shell: process.platform === 'win32',
    env: { ...process.env, CI: '1', NO_COLOR: '1' },
  })
}, { timeout: 240000 })

Then('the Billing page unit tests under {string} run and pass', (world, testDir) => {
  const out = `${world.run.stdout}\n${world.run.stderr}`
  expect(world.run.status, out).toBe(0)
  expect(out).toContain(`${testDir}pages/Billing.test.jsx`)
  expect(out).toMatch(/Tests\s+\d+ passed/)
  expect(out).not.toMatch(/\d+ failed/)
})

Then('the line coverage of the changed Billing page code meets unitTestCoverageMin', (world) => {
  const { thresholds } = JSON.parse(readFileSync(path.join(repoRoot, 'tests/.evals/config.json'), 'utf8'))
  const summary = JSON.parse(readFileSync(path.join(world.coverageDir, 'coverage-summary.json'), 'utf8'))
  const key = Object.keys(summary).find((k) => k.replaceAll('\\', '/').endsWith('src/pages/Billing.jsx'))
  expect(summary[key].lines.pct).toBeGreaterThanOrEqual(thresholds.unitTestCoverageMin)
})

// ---------------------------------------------------------------- cycle journeys (real backend)

Given('the backend is running with its seeded in-memory data', async (world) => {
  const base = process.env.AIRE_BACKEND_URL
  expect(base, 'AIRE_BACKEND_URL points at the running FastAPI backend').toBeTruthy()
  world.requests.length = 0
  vi.stubGlobal('fetch', realBackendFetch(base, world.requests))
  const res = await globalThis.__aireNativeFetch(new URL('/openapi.json', base))
  expect(res.ok).toBe(true)
})

Given('a registered user {string} with password {string} exists on the {string} plan at {string}', async (world, email, password, plan, price) => {
  const base = process.env.AIRE_BACKEND_URL
  const native = globalThis.__aireNativeFetch
  const login = await native(new URL('/api/auth/login', base), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  })
  expect(login.status).toBe(200)
  const billing = await (await native(new URL(`/api/billing?email=${encodeURIComponent(email)}`, base))).json()
  expect(billing.plan_name).toBe(plan)
  expect(billing.price).toBe(price)
})

When('the user logs in as {string} with password {string}', async (world, email, password) => {
  mountApp(world, '/login')
  const user = userEvent.setup()
  const emailInput = document.querySelector('input[type="email"]')
  const passwordInput = document.querySelector('input[type="password"]')
  await user.clear(emailInput)
  await user.type(emailInput, email)
  await user.clear(passwordInput)
  await user.type(passwordInput, password)
  await user.click(screen.getByRole('button', { name: 'Sign In' }))
})

When('the user opens the Billing page', async (world) => {
  await waitFor(() => expect(window.location.pathname).toBe('/billing'), { timeout: 5000 })
  await waitForBilling()
  await waitFor(() => expect(priceText()).toBeTruthy())
  world.loadedRequestCount = world.requests.length
})

Then('the current plan shows {string} at {string}', async (world, plan, price) => {
  await waitFor(() => expect(priceText()).toBe(price), { timeout: 5000 })
  expect(badgeText()).toBe(plan)
})

Then('no request was sent to the backend after the Billing page loaded', (world) => {
  expect(world.requests.slice(world.loadedRequestCount)).toEqual([])
})

Then('the user is still logged in', () => {
  expect(window.location.pathname).toBe('/billing')
  expect(screen.getByRole('button', { name: 'Logout' })).toBeInTheDocument()
})
