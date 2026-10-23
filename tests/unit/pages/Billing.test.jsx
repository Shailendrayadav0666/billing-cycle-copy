import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import Billing from '../../../src/frontend/src/pages/Billing.jsx'

vi.mock('../../../src/frontend/src/context/AuthContext', () => ({
  useAuth: () => ({ token: 'tpg@example.com' }),
}))

const standardBilling = () => ({
  plan_name: 'Standard',
  price: '$20/month',
  renew_at: 'Oct 30, 2026',
  usages: [
    { id: 'video-quality', label: 'Video quality', type: 'feature', value: 'Full HD (1080p)', help: 'Standard video help' },
    { id: 'screens', label: 'Watch at the same time', type: 'feature', value: 'Can watch on 2 devices at once', help: 'Screens help' },
    { id: 'downloads', label: 'Download on devices', type: 'feature', value: 'Can download on 2 devices', help: 'Downloads help' },
  ],
  included_usage: {
    title: 'Plan perks',
    items: [
      { id: 'ad-free', label: 'Ad-free streaming', used_percent: 100 },
      { id: 'spatial-audio', label: 'Spatial audio (select titles)', used_percent: 100 },
    ],
    help: 'Perks included in your Standard plan.',
  },
})

let fetchMock

function stubBilling(billing) {
  fetchMock = vi.fn(() => Promise.resolve({ json: () => Promise.resolve(billing) }))
  vi.stubGlobal('fetch', fetchMock)
}

async function renderLoaded(billing = standardBilling()) {
  stubBilling(billing)
  const view = render(<Billing />)
  await screen.findByText('Plan & Billing')
  return view
}

const upgradeButton = () => screen.queryByRole('button', { name: 'Upgrade to Premium' })

describe('Billing page — existing display (AC-9 regression)', () => {
  beforeEach(() => stubBilling(standardBilling()))

  it('shows the loading state and no upgrade button before data arrives (AC-2)', () => {
    vi.stubGlobal('fetch', vi.fn(() => new Promise(() => {})))
    render(<Billing />)
    expect(screen.getByText('Loading billing...')).toBeInTheDocument()
    expect(upgradeButton()).not.toBeInTheDocument()
  })

  it('renders the Standard plan exactly as before', async () => {
    await renderLoaded()
    expect(screen.getByText('Manage your plan and payments')).toBeInTheDocument()
    expect(screen.getByText('Monthly plan')).toBeInTheDocument()
    expect(screen.getByText('$20/month')).toBeInTheDocument()
    expect(screen.getByText('Active')).toBeInTheDocument()
    expect(screen.getByText('Oct 30, 2026')).toBeInTheDocument()
    expect(screen.getByText('Full HD (1080p)')).toBeInTheDocument()
    expect(screen.getByText('Can watch on 2 devices at once')).toBeInTheDocument()
    expect(screen.getByText('Can download on 2 devices')).toBeInTheDocument()
    expect(screen.getByText('Ad-free streaming')).toBeInTheDocument()
    expect(screen.getByText('Spatial audio (select titles)')).toBeInTheDocument()
    expect(screen.queryByText('Dolby Vision (select titles)')).not.toBeInTheDocument()
    expect(screen.queryByText("You're now on Premium!")).not.toBeInTheDocument()
  })

  it('fetches billing once for the logged-in user', async () => {
    await renderLoaded()
    expect(fetchMock).toHaveBeenCalledTimes(1)
    expect(fetchMock).toHaveBeenCalledWith('/api/billing?email=tpg%40example.com')
  })
})

describe('Plan labels follow the billing data (AC-3)', () => {
  it('reads Standard for a Standard plan', async () => {
    await renderLoaded()
    expect(screen.getByText('Standard', { selector: '.standard-badge' })).toBeInTheDocument()
    expect(screen.getByText("What's included with Standard")).toBeInTheDocument()
  })

  it('reads whatever plan the data names, keeping the badge styling', async () => {
    await renderLoaded({ ...standardBilling(), plan_name: 'Premium' })
    const badge = screen.getByText('Premium', { selector: 'span' })
    expect(badge).toHaveClass('standard-badge')
    expect(screen.getByText("What's included with Premium")).toBeInTheDocument()
  })
})

describe('Upgrade button visibility (AC-1, AC-2)', () => {
  it('is shown for the Standard plan, after the plan row and before the section title', async () => {
    const { container } = await renderLoaded()
    const button = upgradeButton()
    expect(button).toBeInTheDocument()
    expect(button).toHaveAttribute('type', 'button')
    expect(button).toHaveClass('btn', 'upgrade-btn')
    expect(button.previousElementSibling).toBe(container.querySelector('.plan-row'))
    expect(button.nextElementSibling).toHaveClass('section-title')
  })

  it.each(['Premium', 'Basic'])('is not shown for the %s plan', async (plan) => {
    await renderLoaded({ ...standardBilling(), plan_name: plan })
    expect(upgradeButton()).not.toBeInTheDocument()
  })
})

describe('Upgrading to Premium (AC-4 to AC-7)', () => {
  it('switches price, usage cards and perks to Premium (AC-4)', async () => {
    await renderLoaded()
    await userEvent.click(upgradeButton())
    expect(screen.getByText('$40/month')).toBeInTheDocument()
    expect(screen.queryByText('$20/month')).not.toBeInTheDocument()
    expect(screen.getByText('4K Ultra HD')).toBeInTheDocument()
    expect(screen.getByText('Can watch on 4 devices at once')).toBeInTheDocument()
    expect(screen.getByText('Can download on 6 devices')).toBeInTheDocument()
    expect(screen.getByText('Ad-free streaming')).toBeInTheDocument()
    expect(screen.getByText('Spatial audio (select titles)')).toBeInTheDocument()
    expect(screen.getByText('Dolby Vision (select titles)')).toBeInTheDocument()
  })

  it('keeps the renewal date from the billing data (AC-5)', async () => {
    await renderLoaded({ ...standardBilling(), renew_at: 'Nov 22, 2026' })
    await userEvent.click(upgradeButton())
    expect(screen.getByText('Nov 22, 2026')).toBeInTheDocument()
  })

  it('confirms the upgrade, removes the button and relabels the plan (AC-6)', async () => {
    await renderLoaded()
    await userEvent.click(upgradeButton())
    const message = screen.getByRole('status')
    expect(message).toHaveTextContent("You're now on Premium!")
    expect(message).toHaveClass('upgrade-success')
    expect(upgradeButton()).not.toBeInTheDocument()
    expect(screen.getByText('Premium', { selector: '.standard-badge' })).toBeInTheDocument()
    expect(screen.getByText("What's included with Premium")).toBeInTheDocument()
  })

  it('makes no further request and writes nothing to storage (AC-7)', async () => {
    const setItem = vi.spyOn(Storage.prototype, 'setItem')
    await renderLoaded()
    await userEvent.click(upgradeButton())
    expect(fetchMock).toHaveBeenCalledTimes(1)
    expect(setItem).not.toHaveBeenCalled()
  })

  it('is not persisted: a remount re-fetches and shows Standard again (AC-7)', async () => {
    const { unmount } = await renderLoaded()
    await userEvent.click(upgradeButton())
    unmount()
    await renderLoaded()
    expect(screen.getByText('$20/month')).toBeInTheDocument()
    expect(upgradeButton()).toBeInTheDocument()
    expect(screen.queryByRole('status')).not.toBeInTheDocument()
  })
})

describe('Keyboard and screen-reader access (AC-8)', () => {
  it.each(['{Enter}', ' '])('upgrades when the focused button is activated with %s', async (key) => {
    await renderLoaded()
    const user = userEvent.setup()
    await user.tab()
    expect(upgradeButton()).toHaveFocus()
    await user.keyboard(key)
    await waitFor(() => expect(screen.getByText('$40/month')).toBeInTheDocument())
    expect(screen.getByRole('status')).toHaveTextContent("You're now on Premium!")
  })
})
