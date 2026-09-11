import React from 'react'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import Billing from '../../../src/frontend/src/pages/Billing.jsx'
import { useAuth } from '../../../src/frontend/src/context/AuthContext.jsx'

vi.mock('../../../src/frontend/src/context/AuthContext.jsx', () => ({
  useAuth: vi.fn(),
}))

const STANDARD_BILLING = {
  plan_name: 'Standard',
  price: '$20/month',
  renew_at: 'Oct 09, 2026',
  usages: [],
  included_usage: { title: 'Your included usage', items: [], help: '' },
  on_demand_usage: { title: 'On-demand usage', remaining_balance: '$0.00', your_usage: '$0.00', help: '', notice: 'not available' },
}

const PREMIUM_BILLING = { ...STANDARD_BILLING, plan_name: 'Premium', price: '$40/month' }

const PREVIEW = {
  current_plan: 'Standard',
  new_plan: 'Premium',
  days_remaining: 15,
  prorated_charge: 10.0,
  next_renewal_price: 40.0,
  renew_at: 'Oct 09, 2026',
}

function mockFetchSequence(responses) {
  let call = 0
  global.fetch = vi.fn(() => {
    const entry = responses[Math.min(call, responses.length - 1)]
    call += 1
    return Promise.resolve({
      ok: entry.ok !== false,
      status: entry.status ?? 200,
      json: () => Promise.resolve(entry.body),
    })
  })
}

beforeEach(() => {
  useAuth.mockReturnValue({ token: 'tpg@example.com' })
})

// AC2
describe('plan badge', () => {
  it('renders the real plan name instead of a hardcoded value', async () => {
    mockFetchSequence([{ body: STANDARD_BILLING }])
    render(<Billing />)
    await waitFor(() => expect(screen.getByText('Standard', { selector: '.standard-badge' })).toBeInTheDocument())
  })
})

// AC1 / AC8
describe('upgrade CTA visibility', () => {
  it('shows the Upgrade to Premium CTA for a Standard subscriber', async () => {
    mockFetchSequence([{ body: STANDARD_BILLING }])
    render(<Billing />)
    await waitFor(() => expect(screen.getByText('Upgrade to Premium')).toBeInTheDocument())
  })

  it('hides the CTA for a Premium subscriber (already-Premium guard)', async () => {
    mockFetchSequence([{ body: PREMIUM_BILLING }])
    render(<Billing />)
    await waitFor(() => expect(screen.getByText('Premium', { selector: '.standard-badge' })).toBeInTheDocument())
    expect(screen.queryByText('Upgrade to Premium')).not.toBeInTheDocument()
  })
})

// AC3
describe('confirmation modal', () => {
  it('opens on CTA click and shows the exact prorated charge from the backend', async () => {
    mockFetchSequence([{ body: STANDARD_BILLING }, { body: PREVIEW }])
    render(<Billing />)
    await waitFor(() => screen.getByText('Upgrade to Premium'))
    fireEvent.click(screen.getByText('Upgrade to Premium'))
    await waitFor(() => expect(screen.getByText(/10\.00/)).toBeInTheDocument())
    expect(screen.getByText(/15/)).toBeInTheDocument()
  })

  it('cancel closes the modal without calling the upgrade endpoint', async () => {
    mockFetchSequence([{ body: STANDARD_BILLING }, { body: PREVIEW }])
    render(<Billing />)
    await waitFor(() => screen.getByText('Upgrade to Premium'))
    fireEvent.click(screen.getByText('Upgrade to Premium'))
    await waitFor(() => screen.getByText('Cancel'))
    fireEvent.click(screen.getByText('Cancel'))
    expect(screen.queryByText('Confirm Upgrade')).not.toBeInTheDocument()
    expect(global.fetch).toHaveBeenCalledTimes(2) // billing + preview only, never /upgrade
  })
})

// AC5/AC6/AC12
describe('confirm upgrade — success', () => {
  it('shows a success banner and refreshes the plan on success', async () => {
    mockFetchSequence([
      { body: STANDARD_BILLING },
      { body: PREVIEW },
      { body: { status: 'success', plan: 'Premium', charge: 10.0 } },
      { body: PREMIUM_BILLING },
    ])
    render(<Billing />)
    await waitFor(() => screen.getByText('Upgrade to Premium'))
    fireEvent.click(screen.getByText('Upgrade to Premium'))
    await waitFor(() => screen.getByText('Confirm Upgrade'))
    fireEvent.click(screen.getByText('Confirm Upgrade'))
    await waitFor(() => expect(screen.getByText(/You're now on Premium/)).toBeInTheDocument())
    expect(screen.queryByText('Confirm Upgrade')).not.toBeInTheDocument()
  })
})

// AC7
describe('confirm upgrade — declined', () => {
  it('shows an inline error and keeps the user on Standard', async () => {
    mockFetchSequence([
      { body: STANDARD_BILLING },
      { body: PREVIEW },
      { ok: false, status: 402, body: { detail: 'card_declined', message: 'Your card was declined.' } },
    ])
    render(<Billing />)
    await waitFor(() => screen.getByText('Upgrade to Premium'))
    fireEvent.click(screen.getByText('Upgrade to Premium'))
    await waitFor(() => screen.getByText('Confirm Upgrade'))
    fireEvent.click(screen.getByText('Confirm Upgrade'))
    await waitFor(() => expect(screen.getByText(/Payment failed/)).toBeInTheDocument())
    expect(screen.getByText('Confirm Upgrade')).toBeInTheDocument() // modal stays open
  })
})
