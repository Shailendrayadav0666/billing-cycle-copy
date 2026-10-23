# Integration Test Steps: Story 1.1 Upgrade to Premium on the Billing page (frontend only)

**Purpose**: verify, from outside the system, the boundary between the SPA and the backend `GET /api/billing` endpoint. Billing data is fetched once on load, the upgrade makes no request, and a reload fetches again.
**Scope**: AC-7, AC-4, AC-9.
**Boundary under test**: StreamPlex SPA (port 5173), proxied to the FastAPI backend (port 8000), `GET /api/billing?email=<token>`. Source: Atlas deep dive, Flow 4. No application source code was read.

## System Under Test
| Item | Value |
|------|-------|
| Branch | `epic/7344-premium-upgrade-demo-frontend-only` |
| This story's PR | TO CONFIRM: the `[STORY]` PR for Story 1.1, which must be MERGED into the epic branch before execution |
| Confirm the story is in the build | `git log --oneline \| grep -i "1.1"` |
| How to build & run it | **Follow the project's own build docs** (README / CONTRIBUTING / Makefile). This plan does not restate them. |
| Local base URL / port | `http://localhost:5173` (SPA); backend `http://localhost:8000` (API; Swagger at `http://localhost:8000/docs`) |
| Local services that must be up | Backend API on 8000 and frontend dev server on 5173 |
| Test data / accounts to seed | None. Demo user `tpg@example.com` / `password`. |

> If the build or local run fails, that is a **blocker on the dev team**. Report it and do not log functional failures against a system that never started.

---

### TC-INT-01: Billing data is fetched exactly once, and the upgrade sends no request

| Field | Value |
|-------|-------|
| **Traces to** | AC-7 / REQ-NF-01 |
| **Type** | Integration |
| **Priority** | P1 |
| **Preconditions** | Logged in as the demo user. Browser DevTools open on the **Network** tab, filter **All**, "Preserve log" OFF. |
| **Test data** | `tpg@example.com` / `password` |

**Steps**
1. With the Network tab open, navigate to the Billing page (or reload it) and wait for the plan to display.
2. Count the requests whose URL contains `/api/` (expected: one `billing?email=...` request with status 200).
3. Click **Clear** in the Network tab (the clear-log icon).
4. Click **Upgrade to Premium** and wait 5 seconds.
5. Inspect the Network tab.

**Expected result**
- Step 2: exactly **one** request to `/api/billing?email=...`, status **200**.
- Step 5: **no** new requests of any kind (no XHR, fetch, document or other request, including none to `/api/`). The Network tab stays empty.

**Pass/Fail criteria**: PASS only if zero requests are recorded after the click.
**Cleanup**: reload the page.

### TC-INT-02: A reload re-fetches billing from the backend and shows the backend's plan

| Field | Value |
|-------|-------|
| **Traces to** | AC-7 / REQ-F-10, REQ-NF-01 |
| **Type** | Integration |
| **Priority** | P1 |
| **Preconditions** | Logged in as the demo user, upgraded to Premium in the page (TC-INT-01 completed). Network tab open. |
| **Test data** | `tpg@example.com` / `password` |

**Steps**
1. Reload the Billing page.
2. In the Network tab, select the `/api/billing?email=...` request and open its **Response** preview.
3. Compare `plan_name` and `price` in the response with the page.

**Expected result**
- One new `/api/billing` request is made (status 200).
- The response shows `plan_name` **"Standard"** and `price` **"$20/month"**, so the backend was never told about the upgrade.
- The page shows Standard and $20/month, matching the response.

**Pass/Fail criteria**: PASS if the backend still reports Standard and the page matches it.
**Cleanup**: none.

### TC-INT-03: Backend billing contract is unchanged

| Field | Value |
|-------|-------|
| **Traces to** | AC-9, AC-7 / REQ-NF-01, REQ-NF-02 |
| **Type** | Integration |
| **Priority** | P2 |
| **Preconditions** | Backend running on port 8000 |
| **Test data** | Email query value `tpg@example.com` |

**Steps**
1. In a browser, open `http://localhost:8000/api/billing?email=tpg@example.com` (or use Swagger UI at `/docs`, "Try it out").
2. Read the JSON response.

**Expected result**
- Status **200**, with a JSON object containing `plan_name`, `price`, `renew_at`, `usages` (an array of 3) and `included_usage` (with `title`, `items` and `help`).
- Values: `plan_name` "Standard", `price` "$20/month", `renew_at` "Oct 30, 2026"; `included_usage.items` contains "Ad-free streaming" and "Spatial audio (select titles)".
- There is no Premium field or new key; the response shape is the same as documented in the Atlas deep dive Flow 4.

**Pass/Fail criteria**: PASS if the shape and values match. Any new, removed or renamed field is a FAIL.
**Cleanup**: none.

### TC-INT-04: Premium values render correctly alongside the backend-provided renewal date

| Field | Value |
|-------|-------|
| **Traces to** | AC-4, AC-5 / REQ-F-03, REQ-F-04 |
| **Type** | Integration |
| **Priority** | P2 |
| **Preconditions** | Backend freshly started. Register a new user so that their `renew_at` comes from the backend as "today + 30 days". |
| **Test data** | New user `QA Renew`, `qa.renew+<timestamp>@example.com`, password `Passw0rd!` |

**Steps**
1. Register and log in as the new user, then open Billing.
2. Note the "Renew at" date (expected about 30 days from today, formatted like "Nov 22, 2026").
3. Click **Upgrade to Premium**.
4. Read the price and the "Renew at" date.

**Expected result**
- The price changes to **$40/month**.
- The "Renew at" date remains exactly the backend-provided date from step 2. It is not replaced by a hardcoded value such as "Oct 30, 2026".

**Pass/Fail criteria**: PASS if the renewal date is unchanged for a user whose date differs from the demo user's.
**Cleanup**: restart the backend to discard the user.

### TC-INT-05: The frontend unit-test suite runs from a clean install

| Field | Value |
|-------|-------|
| **Traces to** | AC-10 / REQ-NF-04 |
| **Type** | Integration |
| **Priority** | P2 |
| **Preconditions** | Epic branch checked out after the Story 1.1 merge; no `src/frontend/node_modules` folder present (delete it first if it exists) |
| **Test data** | None |

**Steps**
1. In `src/frontend`, install dependencies from the lock file per the project's build docs (`npm ci`).
2. Run `npm test`.
3. Read the summary printed by the test runner.

**Expected result**
- `npm test` runs to completion without interactive prompts and exits successfully (exit code 0).
- The output lists the Billing page test file(s) from the repo-root `tests/unit/` folder, all passing, with 0 failed.

**Pass/Fail criteria**: PASS if the suite runs from a clean install, picks up `tests/unit/`, and every test passes.
**Cleanup**: none.
