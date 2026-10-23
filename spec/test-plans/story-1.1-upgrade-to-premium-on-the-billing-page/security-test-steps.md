# Security Test Steps: Story 1.1 Upgrade to Premium on the Billing page (frontend only)

**Purpose**: verify that the story introduces no new security exposure. The added dev tooling must follow the supply-chain rule, the upgrade must not persist or leak anything, and authentication must be unaffected.
**Scope**: AC-10 (SECURITY-10 / REQ-NF-05), AC-7 (no persistence), AC-9 (auth regression).
**Derived from**: Story 1.1 acceptance criteria, `requirements.md` REQ-NF-05 and the Security Baseline. No application source code was read. Checks are made on the repository's committed dependency manifests and from the browser, as observable artifacts.

## System Under Test
| Item | Value |
|------|-------|
| Branch | `epic/7344-premium-upgrade-demo-frontend-only` |
| This story's PR | TO CONFIRM: the `[STORY]` PR for Story 1.1, which must be MERGED into the epic branch before execution |
| Confirm the story is in the build | `git log --oneline \| grep -i "1.1"` |
| How to build & run it | **Follow the project's own build docs** (README / CONTRIBUTING / Makefile). This plan does not restate them. |
| Local base URL / port | `http://localhost:5173` |
| Local services that must be up | Backend API on 8000 and frontend dev server on 5173 (TC-SEC-03 and 04 only) |
| Test data / accounts to seed | None. Demo user `tpg@example.com` / `password`. |

> If the build or local run fails, that is a **blocker on the dev team**. Report it and do not log functional failures against a system that never started.

Pre-existing weaknesses recorded by Atlas (for example the email used as the token, and the token stored in localStorage) are **out of scope**. These cases only check that this story does not add to them.

---

### TC-SEC-01: New test tooling is dev-only, exact-pinned, and lock-file backed (SECURITY-10)

| Field | Value |
|-------|-------|
| **Traces to** | AC-10 / REQ-NF-05, REQ-NF-04 |
| **Type** | Security |
| **Priority** | P1 |
| **Preconditions** | Epic branch checked out after the Story 1.1 merge |
| **Test data** | The Story 1.1 merge commit: `git show --stat <merge-commit>` |

**Steps**
1. Run `git show <story-1.1-merge-commit> -- src/frontend/package.json` and read the dependency changes.
2. Confirm `src/frontend/package-lock.json` also changed in the same story (`git show --stat`).
3. For each newly added package (expected: Vitest, React Testing Library and jsdom, plus any Vitest coverage helper), note which section it was added to and its version string.
4. In `src/frontend/package-lock.json`, check the `resolved` URL of each new package.

**Expected result**
- Every new package is under **devDependencies**, and **none** is added to `dependencies`.
- Every new version is an **exact** version (for example `3.2.4`) with **no** `^`, `~`, `*` or `latest`.
- `package-lock.json` is updated and committed in the same story.
- Every `resolved` URL points to `https://registry.npmjs.org/`.

**Pass/Fail criteria**: PASS only if all four hold.
**Cleanup**: none.

### TC-SEC-02: No known high or critical vulnerabilities in the added packages (SECURITY-10)

| Field | Value |
|-------|-------|
| **Traces to** | AC-10 / REQ-NF-05 |
| **Type** | Security |
| **Priority** | P2 |
| **Preconditions** | Dependencies installed from the lock file in `src/frontend` (`npm ci`, per the project's build docs) |
| **Test data** | None |

**Steps**
1. In `src/frontend`, run `npm audit --omit=optional`.
2. Note any findings for the newly added test packages and their transitive dependencies.

**Expected result**
- **0 critical** and **0 high** vulnerabilities attributable to the packages added by Story 1.1.

**Pass/Fail criteria**: PASS if there are no critical or high findings introduced by the story. Pre-existing findings in older packages are recorded but do not fail this case.
**Cleanup**: none.

### TC-SEC-03: The upgrade writes nothing to browser storage or cookies

| Field | Value |
|-------|-------|
| **Traces to** | AC-7 / REQ-F-10, REQ-NF-01 |
| **Type** | Security |
| **Priority** | P2 |
| **Preconditions** | Logged in as the demo user on the Billing page. DevTools open on **Application** (Chrome) or **Storage** (Firefox). |
| **Test data** | `tpg@example.com` / `password` |

**Steps**
1. Record every Local Storage, Session Storage and Cookie entry for `http://localhost:5173`.
2. Click **Upgrade to Premium**.
3. Refresh the storage panes and compare.

**Expected result**
- No entry is added, removed or changed by the upgrade. In particular, nothing containing "Premium" or plan data appears in any storage, and the existing auth entry is unchanged.

**Pass/Fail criteria**: PASS if storage and cookies are identical before and after the click.
**Cleanup**: reload the page.

### TC-SEC-04: Nothing sensitive is logged to the browser console during the upgrade

| Field | Value |
|-------|-------|
| **Traces to** | AC-9, AC-7 / REQ-NF-02 |
| **Type** | Security |
| **Priority** | P3 |
| **Preconditions** | DevTools **Console** open with "Preserve log" ON, logged in as the demo user on Billing |
| **Test data** | `tpg@example.com` / `password` |

**Steps**
1. Clear the console.
2. Reload Billing, then click **Upgrade to Premium**.
3. Read every console message.

**Expected result**
- No console message contains the user's email or token, a password, or a dump of the billing object.
- No uncaught errors or React warnings are shown.

**Pass/Fail criteria**: PASS if the console has no sensitive output and no errors.
**Cleanup**: turn "Preserve log" off.
