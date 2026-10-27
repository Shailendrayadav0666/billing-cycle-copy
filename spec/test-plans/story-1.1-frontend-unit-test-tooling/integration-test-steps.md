# Integration Test Steps — story-1.1 Frontend unit-test tooling

**Purpose**: confirm the new unit-test toolchain works with the existing frontend project: the runner, the jsdom environment, the Billing page and a mocked billing API.
**Scope**: AC-2, AC-3. Supply-chain checks (AC-1, AC-4) are in `security-test-steps.md`.

## System Under Test
| Item | Value |
|------|-------|
| Branch | `epic/HELIX-7344-premium-upgrade-demo-frontend-only` |
| This story's PR | The `[STORY]` PR for Story 1.1, merged into the epic branch (TO CONFIRM: PR number once raised) |
| Confirm the story is in the build | `git log --oneline \| grep "1.1"` (TO CONFIRM: commit message pattern) |
| How to build & run it | **Follow the project's own build docs** (README / CONTRIBUTING). This plan does not restate them. Only the frontend dependencies need installing; no server has to run. |
| Local base URL / port | Not needed: these cases run commands in `src/frontend/` |
| Local services that must be up | None. The backend must NOT be running, which proves the tests do not depend on it |
| Test data / accounts to seed | None |

> If the dependencies fail to install, that is a **blocker on the dev team**. Report it and do not log the cases below as failed.

### TC-INT-01 — Unit test command passes with the Billing page smoke test

| Field | Value |
|-------|-------|
| **Traces to** | AC-2 / REQ-NF-05 |
| **Type** | Integration |
| **Priority** | P1 |
| **Preconditions** | Epic branch checked out with Story 1.1 merged; frontend dependencies installed per the project's docs; backend NOT running |
| **Test data** | None |

**Steps**
1. Open a terminal in `src/frontend/`.
2. Run `npm run test`.
3. Read the runner output to the end.

**Expected result**
- The output identifies the test runner as Vitest and reports a jsdom test environment (or names jsdom in its configuration summary).
- At least one test that renders the Billing page is listed and passes. For example, it finds the "Plan & Billing" heading.
- The command finishes with exit status 0 (`echo $?` prints `0`).

**Pass/Fail criteria**: PASS if a Billing page test is listed as passed and the exit status is 0. Anything else is a FAIL.
**Cleanup**: None.

### TC-INT-02 — Tests never reach a real billing API

| Field | Value |
|-------|-------|
| **Traces to** | AC-2 / REQ-NF-05 |
| **Type** | Integration |
| **Priority** | P2 |
| **Preconditions** | As TC-INT-01. The backend on port 8000 is stopped, and nothing else listens on port 8000. |
| **Test data** | None |

**Steps**
1. Confirm nothing listens on port 8000 (for example, `curl http://localhost:8000/docs` fails to connect).
2. In `src/frontend/`, run `npm run test`.

**Expected result**
- The test run passes exactly as in TC-INT-01, even though no billing API is reachable.
- The output shows no connection-refused or network error coming from a test.

**Pass/Fail criteria**: PASS if the suite passes with no API running. A failure or network error caused by a missing API is a FAIL.
**Cleanup**: None.

### TC-INT-03 — Coverage command prints a summary and writes an lcov report

| Field | Value |
|-------|-------|
| **Traces to** | AC-3 / REQ-NF-05 |
| **Type** | Integration |
| **Priority** | P1 |
| **Preconditions** | As TC-INT-01. Delete any existing `src/frontend/coverage/` folder first. |
| **Test data** | None |

**Steps**
1. In `src/frontend/`, delete the `coverage/` folder if it exists.
2. Run `npm run test:coverage`.
3. List the contents of `src/frontend/coverage/`.

**Expected result**
- A text coverage table (statements / branches / functions / lines per file) is printed to the terminal.
- The file `src/frontend/coverage/lcov.info` exists and is not empty.
- The command finishes with exit status 0.

**Pass/Fail criteria**: PASS if both the text summary and a non-empty `lcov.info` are produced. Anything else is a FAIL.
**Cleanup**: Delete `src/frontend/coverage/`.

### TC-INT-04 — Coverage output is not picked up by git

| Field | Value |
|-------|-------|
| **Traces to** | AC-3 / REQ-NF-05 |
| **Type** | Integration |
| **Priority** | P3 |
| **Preconditions** | TC-INT-03 has just been run, so `src/frontend/coverage/` exists |
| **Test data** | None |

**Steps**
1. From the repo root, run `git status --porcelain src/frontend/coverage`.

**Expected result**
- No line is printed for `src/frontend/coverage/`: the generated report is ignored and cannot be committed by accident.

**Pass/Fail criteria**: PASS if the coverage folder does not appear as untracked or modified. FAIL if it does.
**Cleanup**: Delete `src/frontend/coverage/`.
