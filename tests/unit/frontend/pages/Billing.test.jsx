import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { cleanup, render, screen } from '@testing-library/react'
import Billing from '../../../../src/frontend/src/pages/Billing.jsx'

vi.mock('../../../../src/frontend/src/context/AuthContext.jsx', () => ({
  useAuth: () => ({ token: 'tpg@example.com' }),
}))

// Same shape as the backend's GET /api/billing response for the Standard plan.
const standardBilling = {
  plan_name: 'Standard',
  price: '$20/month',
  renew_at: 'Oct 30, 2026',
  usages: [
    {
      id: 'video-quality',
      label: 'Video quality',
      type: 'feature',
      value: 'Full HD (1080p)',
      help: 'The best video resolution available on the Standard plan.',
    },
    {
      id: 'screens',
      label: 'Watch at the same time',
      type: 'feature',
      value: 'Can watch on 2 devices at once',
      help: 'Number of supported devices that can stream on your account simultaneously.',
    },
    {
      id: 'downloads',
      label: 'Download on devices',
      type: 'feature',
      value: 'Can download on 2 devices',
      help: 'Number of supported devices you can download titles to for offline viewing.',
    },
  ],
  included_usage: {
    title: 'Plan perks',
    items: [
      { id: 'ad-free', label: 'Ad-free streaming', used_percent: 100 },
      { id: 'spatial-audio', label: 'Spatial audio (select titles)', used_percent: 100 },
    ],
    help: 'Perks included in your Standard plan.',
  },
}

let fetchMock

beforeEach(() => {
  fetchMock = vi.fn(() =>
    Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve(standardBilling) }),
  )
  vi.stubGlobal('fetch', fetchMock)
})

afterEach(() => {
  cleanup()
  vi.unstubAllGlobals()
})

describe('Billing page smoke test', () => {
  it('runs in the jsdom environment', () => {
    expect(navigator.userAgent).toContain('jsdom')
    expect(document.body).toBeDefined()
  })

  it('renders the Billing page against a mocked /api/billing response (plan_name "Standard", price "$20/month") and finds the "Plan & Billing" heading', async () => {
    render(<Billing />)

    expect(await screen.findByRole('heading', { name: 'Plan & Billing' })).toBeDefined()
    expect(screen.getByText('$20/month')).toBeDefined()
    expect(screen.getByText('Standard')).toBeDefined()
  })

  it('uses only the mocked /api/billing response and never calls the real endpoint', async () => {
    render(<Billing />)
    await screen.findByRole('heading', { name: 'Plan & Billing' })

    expect(vi.isMockFunction(globalThis.fetch)).toBe(true)
    expect(fetchMock).toHaveBeenCalledTimes(1)
    expect(fetchMock).toHaveBeenCalledWith('/api/billing?email=tpg%40example.com')
  })

  it('shows the loading text until the billing response arrives', async () => {
    render(<Billing />)

    expect(screen.getByText('Loading billing...')).toBeDefined()
    await screen.findByRole('heading', { name: 'Plan & Billing' })
    expect(screen.queryByText('Loading billing...')).toBeNull()
  })
})
