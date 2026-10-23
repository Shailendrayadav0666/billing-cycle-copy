// Backends the behaviour scenarios run against, both reached through the SPA's own fetch calls.
//
// - FakeBackend: an in-memory model of the documented StreamPlex API contract (Atlas deep dive,
//   Flows 1-4: POST /api/auth/login, GET /api/users/me, GET /api/billing). Used by the work-unit
//   contracts, whose scenarios need plans the real backend cannot seed (Premium, Basic, pending).
// - realBackendFetch: forwards to the running FastAPI backend at AIRE_BACKEND_URL. Used by the
//   cycle-level journeys in spec/behavior.feature.
//
// Both record every request so scenarios can assert that the upgrade makes no call.

const json = (status, body) =>
  Promise.resolve({ ok: status >= 200 && status < 300, status, json: () => Promise.resolve(body) })

export class FakeBackend {
  constructor() {
    this.requests = []
    this.users = { 'tpg@example.com': { id: 1, name: 'TPG', email: 'tpg@example.com', password: 'password' } }
    this.billing = {}
    this.pending = false
  }

  setBilling(email, billing) {
    this.billing[email] = billing
  }

  fetch = (input, init = {}) => {
    const url = new URL(String(input), 'http://localhost')
    const method = (init.method || 'GET').toUpperCase()
    this.requests.push({ method, path: url.pathname, query: url.search })
    const email = url.searchParams.get('email')
    if (method === 'POST' && url.pathname === '/api/auth/login') {
      const { email: e, password } = JSON.parse(init.body)
      const user = this.users[e]
      if (!user || user.password !== password) return json(401, { detail: 'Invalid credentials' })
      const { password: _pw, ...safe } = user
      return json(200, { access_token: e, user: safe })
    }
    if (url.pathname === '/api/users/me') {
      const user = this.users[email]
      if (!user) return json(401, { detail: 'Not authenticated' })
      const { password: _pw, ...safe } = user
      return json(200, safe)
    }
    if (url.pathname === '/api/billing') {
      if (this.pending) return new Promise(() => {})
      if (!this.users[email]) return json(401, { detail: 'Not authenticated' })
      return json(200, structuredClone(this.billing[email]))
    }
    return json(404, { detail: 'Not Found' })
  }
}

export function realBackendFetch(baseUrl, requests) {
  const nativeFetch = globalThis.__aireNativeFetch
  return (input, init = {}) => {
    const url = new URL(String(input), baseUrl)
    requests.push({ method: (init.method || 'GET').toUpperCase(), path: url.pathname, query: url.search })
    return nativeFetch(url, init)
  }
}
