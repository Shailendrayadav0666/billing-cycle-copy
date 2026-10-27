# Security Test Steps — story-1.1 Frontend unit-test tooling

**Purpose**: confirm the new test libraries follow the Security Baseline supply-chain rule (SECURITY-10): dev-only, from the official registry, pinned in a committed lock file, and audited.
**Scope**: AC-1, AC-4.

## System Under Test
| Item | Value |
|------|-------|
| Branch | `epic/HELIX-7344-premium-upgrade-demo-frontend-only` |
| This story's PR | The `[STORY]` PR for Story 1.1, merged into the epic branch (TO CONFIRM: PR number once raised) |
| Confirm the story is in the build | `git log --oneline \| grep "1.1"` (TO CONFIRM: commit message pattern) |
| How to build & run it | **Follow the project's own build docs** (README / CONTRIBUTING). This plan does not restate them. |
| Local base URL / port | Not needed |
| Local services that must be up | None |
| Test data / accounts to seed | None |

### TC-SEC-01 — Test libraries are devDependencies only

| Field | Value |
|-------|-------|
| **Traces to** | AC-1 / REQ-NF-05, REQ-NF-06, SECURITY-10 |
| **Type** | Security |
| **Priority** | P1 |
| **Preconditions** | Epic branch checked out with Story 1.1 merged |
| **Test data** | None |

**Steps**
1. Open `src/frontend/package.json` in a text viewer.
2. Read the `devDependencies` section.
3. Read the `dependencies` section.

**Expected result**
- `devDependencies` lists `vitest`, `@testing-library/react` and `jsdom`.
- `dependencies` lists only `react`, `react-dom` and `react-router-dom`, exactly as before the story.

**Pass/Fail criteria**: PASS if all three test libraries are under `devDependencies` and none of them is under `dependencies`. Anything else is a FAIL.
**Cleanup**: None.

### TC-SEC-02 — Production build contains no test library

| Field | Value |
|-------|-------|
| **Traces to** | AC-1 / REQ-NF-06, SECURITY-10 |
| **Type** | Security |
| **Priority** | P2 |
| **Preconditions** | As TC-SEC-01; frontend production build produced per the project's build docs (`dist/` folder) |
| **Test data** | Search terms: `vitest`, `testing-library`, `jsdom` |

**Steps**
1. Build the frontend for production, following the project's build docs.
2. Search the files under `src/frontend/dist/` for the text `vitest`, `testing-library` and `jsdom`.

**Expected result**
- None of the three terms appears in any built file.

**Pass/Fail criteria**: PASS if no test library is bundled into the production build. FAIL on any match.
**Cleanup**: Delete `src/frontend/dist/` if it did not exist before.

### TC-SEC-03 — Exact versions are pinned in a committed lock file

| Field | Value |
|-------|-------|
| **Traces to** | AC-4 / REQ-NF-06, SECURITY-10 |
| **Type** | Security |
| **Priority** | P1 |
| **Preconditions** | As TC-SEC-01 |
| **Test data** | None |

**Steps**
1. From the repo root, run `git ls-files src/frontend/package-lock.json`.
2. Run `git check-ignore -v src/frontend/package-lock.json`.
3. Open `src/frontend/package-lock.json` and find the entries for `node_modules/vitest`, `node_modules/@testing-library/react` and `node_modules/jsdom`.

**Expected result**
- Step 1 prints `src/frontend/package-lock.json`, so the file is tracked.
- Step 2 prints nothing, so the file is not ignored.
- Each of the three entries has an exact `version` (for example `"3.2.4"`, not a range) and a `resolved` URL on `https://registry.npmjs.org/`.

**Pass/Fail criteria**: PASS if the lock file is tracked, not ignored, and pins exact versions from the official npm registry. Anything else is a FAIL.
**Cleanup**: None.

### TC-SEC-04 — `npm audit` result is recorded with no high or critical advisory

| Field | Value |
|-------|-------|
| **Traces to** | AC-4 / REQ-NF-06, SECURITY-10 |
| **Type** | Security |
| **Priority** | P1 |
| **Preconditions** | As TC-SEC-01; frontend dependencies installed |
| **Test data** | None |

**Steps**
1. Find the story's evidence under `reports/` for Story 1.1 and open the recorded `npm audit` result (TO CONFIRM: exact evidence file name).
2. In `src/frontend/`, run `npm audit` yourself.
3. Compare the two results.

**Expected result**
- An `npm audit` result exists in the story's evidence.
- Neither result reports a **high** or **critical** advisory for `vitest`, `@testing-library/react`, `jsdom` or their dependencies.

**Pass/Fail criteria**: PASS if the evidence exists and shows no high or critical advisory for the added packages. A missing record, or any high or critical advisory, is a FAIL (raise it with `raise-defect`).
**Cleanup**: None.
