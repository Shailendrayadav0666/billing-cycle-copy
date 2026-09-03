# API & Contract Testing Gate Evidence — Story 1

**Applicability**: this story's plan includes an API Layer Generation step (2 new endpoints) — the gate is MANDATORY.
**Command**: `src/backend/venv/Scripts/python.exe -m pytest tests/unit/test_billing_upgrade_contract.py -v --junitxml=api-contract-test-report.xml`
**Result**: 12/12 passed

## Per-endpoint checklist

### `GET /api/billing/upgrade-preview`
| Checklist item | Test | Result |
|---|---|---|
| Functional / happy path | `test_preview_functional_and_response_code` | PASS |
| Response-code validation | same (200) | PASS |
| Role-based authorization | `test_preview_401_when_unauthenticated` (401) — no roles beyond authenticated/not in this app, so 403 is N/A | PASS |
| Error-response validation | `test_preview_409_error_shape` (`{"detail": "already_premium"}`) | PASS |
| Request validation | `test_preview_missing_required_email_returns_422` | PASS |
| Response contract/schema | `test_preview_response_schema` (exact field set + types) | PASS |

### `POST /api/billing/upgrade`
| Checklist item | Test | Result |
|---|---|---|
| Functional / happy path | `test_upgrade_functional_and_response_code` | PASS |
| Response-code validation | same (200) | PASS |
| Role-based authorization | `test_upgrade_401_when_unauthenticated` (401) — 403 N/A, same reason | PASS |
| Error-response validation | `test_upgrade_409_error_shape`, `test_upgrade_402_error_shape` | PASS |
| Request validation | `test_upgrade_missing_required_email_returns_422`, `test_upgrade_wrong_type_for_email_returns_422` | PASS |
| Response contract/schema | `test_upgrade_success_response_schema` (exact field set + types) | PASS |

## Artifacts
- `api-contract-test-run.log` — raw pytest output
- `api-contract-test-report.xml` — JUnit XML, machine-readable
