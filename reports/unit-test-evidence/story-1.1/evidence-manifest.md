# Unit Test & Coverage Evidence — Story 1.1

## Backend (`src/backend`)
- Command: `pytest ../../tests/unit/backend --cov=. --cov-report=xml --cov-report=term-missing`
- Result: 8/8 passed
- Coverage: 78% of `main.py` overall; **100% of new/changed lines** (constants, `UpgradeRequest`, `charge_card`, `_compute_proration`, both new endpoints). Uncovered lines are all pre-existing (`register`, `me`, `billing`, `tasks`, `add_task` handlers, static-mount check) — not touched by this story.
- Raw log: `unit-test-run-backend.log`
- Machine-readable report: `src/backend/coverage.xml` (cobertura)

## Frontend (`src/frontend`)
- Command: `npm run test` (`vitest run --coverage`)
- Result: 7/7 passed
- Coverage: 76.06% statements / 90.9% branch / 90% funcs of `Billing.jsx` overall. Uncovered lines (23-50, 59-71, 245-262) are pre-existing icon/usage-grid rendering, untouched by this story. **All new code (badge, CTA, modal, confirm/cancel handlers, banner) is exercised.**
- Raw log: `unit-test-run-frontend.log`
- Machine-readable report: `src/frontend/coverage/lcov.info`

## Gate verdict
SH-LOOP-1 (Unit Test & Coverage): **PASS** on attempt 0 (no remediation needed) — coverage on new/changed code is 100% for both stacks, well above `unitTestCoverageMin` (90.0).
