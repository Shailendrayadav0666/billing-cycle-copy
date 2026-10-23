# StreamPlex Frontend

React 19 single-page app (Vite 8) for the StreamPlex Billing-Cycle demo. It talks to the FastAPI
backend in `src/backend/`. During development, Vite proxies every `/api/*` request to
`http://localhost:8000` (see `vite.config.js`).

## Pages

| Route | Page | What it does |
|---|---|---|
| `/login` | `src/pages/Login.jsx` | Sign in or register (demo user: `tpg@example.com` / `password`) |
| `/billing` | `src/pages/Billing.jsx` | Shows the current plan, price, renewal date, usage cards and plan perks, loaded once from `GET /api/billing` |

### Upgrade to Premium (demo)

On the Billing page, a user on the **Standard** plan sees an **Upgrade to Premium** button below the
plan card. Clicking it switches the page to Premium **in local React state only**:

- the plan becomes Premium at $40/month, with 4K Ultra HD, 4 screens and 6 downloads, and adds the Dolby Vision perk
- the renewal date is unchanged
- the message "You're now on Premium!" appears and the button disappears

No request is sent to the backend. Refreshing the page re-fetches the billing data and shows Standard
again. Users on any other plan do not see the button.

## Scripts

Run from `src/frontend/`:

| Command | Purpose |
|---|---|
| `npm install` | Install dependencies (use `npm ci` for a clean, lock-file install) |
| `npm run dev` | Start the dev server on `http://localhost:5173` (start the backend on port 8000 first) |
| `npm run build` | Production build into `dist/` |
| `npm run lint` | Lint with oxlint (`.oxlintrc.json`) |
| `npm test` | Run the unit tests in the repo-root `tests/unit/` (Vitest + React Testing Library, jsdom) |
| `npm run test:coverage` | Unit tests with v8 coverage, written to `coverage/` (lcov, json-summary, HTML) |
| `npm run test:behavior` | Run the Gherkin behaviour specs in the repo-root `spec/behavior/` (QuickPickle, with step definitions in `tests/behavior/steps/`) |

The test files live outside this package, in the repo-root `tests/` tree, but they run with this
package's dependencies and configuration (`vitest.config.js`, `vitest.behavior.config.js`).
