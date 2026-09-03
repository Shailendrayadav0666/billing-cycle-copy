# Unit Test & Coverage Evidence — Story 1

**Command**: `src/backend/venv/Scripts/python.exe -m pytest tests/unit/test_billing_upgrade.py --cov=src/backend --cov-report=term-missing --cov-report=xml -v`
**Result**: 13/13 passed
**Whole-file coverage**: 80% (110 stmts, 22 missed) — `src/backend/main.py`

## Scope note (unitTestCoverageMin applies to new/changed code, not the whole file)

All 22 missed lines fall inside **pre-existing endpoints this story did not touch**: `login` (line 164), `register` (170-227), `me` (232-235), `tasks`/`add_task` (240-260). Confirmed via `git diff main story/1-mid-cycle-subscription-upgrade -- src/backend/main.py` — none of the missed line ranges intersect the diff.

**Coverage on this story's new/changed code** (`PLANS`, `PREMIUM_QUOTAS`, `DAYS_IN_CYCLE`, `UpgradeRequest`, `charge_card()`, `_compute_prorated_charge()`, `GET /api/billing/upgrade-preview`, `POST /api/billing/upgrade`): **100%** — every new statement and branch (already-Premium guard, success path, declined path, unauthenticated path) is exercised by `tests/unit/test_billing_upgrade.py`.

## Bug found and fixed during test-writing
`_compute_prorated_charge` originally used `datetime.today()` (includes time-of-day) against a date-only `renew_at_date`, causing `days_remaining` to be off by one whenever run after midnight (14 instead of 15 in the epic's own worked example). Fixed to compare `.date()` on both sides. This is now covered by `test_prorated_charge_matches_epic_example`.

## Artifacts
- `unit-test-run.log` — raw pytest output
- `coverage-report.xml` — Cobertura XML coverage report
