"""API & Contract Testing Gate (dev-implement.md Step 6.2) for the 2 new endpoints
this story adds: GET /api/billing/upgrade-preview, POST /api/billing/upgrade.

Checklist: functional/happy path, response-code validation, role-based
authorization (401 unauthenticated - this app has no roles beyond
authenticated/not, so 403 is not applicable), error-response validation,
request validation, response contract/schema validation.
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src" / "backend"))

import main  # noqa: E402

client = TestClient(main.app)

EXPECTED_PREVIEW_FIELDS = {
    "current_plan",
    "new_plan",
    "days_remaining",
    "prorated_charge",
    "next_renewal_price",
    "renew_at",
}
EXPECTED_UPGRADE_SUCCESS_FIELDS = {"status", "plan", "charge"}


def _seed(email: str, plan_name: str = "Standard") -> None:
    renew_at = (datetime.today() + timedelta(days=15)).strftime("%b %d, %Y")
    main.users[email] = {
        "id": 999,
        "name": email,
        "email": email,
        "password": "password",
        "plan": plan_name,
        "price": main.PLANS[plan_name]["label"],
        "renew_at": renew_at,
    }
    main.billing_data[email] = {
        "plan_name": plan_name,
        "price": main.PLANS[plan_name]["label"],
        "renew_at": renew_at,
        "usages": [{"id": "chat-credits", "label": "Chat credits", "used": 0, "total": 2000, "help": "h"}],
        "included_usage": {"title": "t", "items": []},
        "on_demand_usage": {"title": "t", "remaining_balance": "$0", "your_usage": "$0", "help": "h", "notice": "n"},
    }


def teardown_function():
    for email in ("contract-user@example.com", "fail@example.com"):
        main.users.pop(email, None)
        main.billing_data.pop(email, None)


# --- Functional / happy path + response-code validation ------------------------------------


def test_preview_functional_and_response_code():
    _seed("contract-user@example.com")
    resp = client.get("/api/billing/upgrade-preview", params={"email": "contract-user@example.com"})
    assert resp.status_code == 200


def test_upgrade_functional_and_response_code():
    _seed("contract-user@example.com")
    resp = client.post("/api/billing/upgrade", json={"email": "contract-user@example.com"})
    assert resp.status_code == 200


# --- Role-based authorization: 401 unauthenticated (no roles in this app -> 403 N/A) --------


def test_preview_401_when_unauthenticated():
    resp = client.get("/api/billing/upgrade-preview", params={"email": "nobody@example.com"})
    assert resp.status_code == 401
    assert resp.json() == {"detail": "Not authenticated"}


def test_upgrade_401_when_unauthenticated():
    resp = client.post("/api/billing/upgrade", json={"email": "nobody@example.com"})
    assert resp.status_code == 401
    assert resp.json() == {"detail": "Not authenticated"}


# --- Error-response validation (standard format + codes) -----------------------------------


def test_preview_409_error_shape():
    _seed("contract-user@example.com", "Premium")
    resp = client.get("/api/billing/upgrade-preview", params={"email": "contract-user@example.com"})
    assert resp.status_code == 409
    assert resp.json() == {"detail": "already_premium"}


def test_upgrade_409_error_shape():
    _seed("contract-user@example.com", "Premium")
    resp = client.post("/api/billing/upgrade", json={"email": "contract-user@example.com"})
    assert resp.status_code == 409
    assert resp.json() == {"detail": "already_premium"}


def test_upgrade_402_error_shape():
    _seed("fail@example.com", "Standard")
    resp = client.post("/api/billing/upgrade", json={"email": "fail@example.com"})
    assert resp.status_code == 402
    body = resp.json()
    assert set(body.keys()) == {"detail", "message"}
    assert body["detail"] == "card_declined"


# --- Request validation (required fields, data types) ---------------------------------------


def test_preview_missing_required_email_returns_422():
    resp = client.get("/api/billing/upgrade-preview")
    assert resp.status_code == 422


def test_upgrade_missing_required_email_returns_422():
    resp = client.post("/api/billing/upgrade", json={})
    assert resp.status_code == 422


def test_upgrade_wrong_type_for_email_returns_422():
    resp = client.post("/api/billing/upgrade", json={"email": 12345})
    assert resp.status_code == 422


# --- Response contract / schema validation ---------------------------------------------------


def test_preview_response_schema():
    _seed("contract-user@example.com")
    resp = client.get("/api/billing/upgrade-preview", params={"email": "contract-user@example.com"})
    body = resp.json()
    assert set(body.keys()) == EXPECTED_PREVIEW_FIELDS
    assert isinstance(body["days_remaining"], int)
    assert isinstance(body["prorated_charge"], (int, float))
    assert isinstance(body["next_renewal_price"], (int, float))
    assert isinstance(body["renew_at"], str)


def test_upgrade_success_response_schema():
    _seed("contract-user@example.com")
    resp = client.post("/api/billing/upgrade", json={"email": "contract-user@example.com"})
    body = resp.json()
    assert set(body.keys()) == EXPECTED_UPGRADE_SUCCESS_FIELDS
    assert body["status"] == "success"
    assert body["plan"] == "Premium"
    assert isinstance(body["charge"], (int, float))
