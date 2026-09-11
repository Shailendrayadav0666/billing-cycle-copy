"""Unit tests for the Mid-Cycle Subscription Upgrade endpoints (Story 1.1)."""
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src" / "backend"))

import pytest
from fastapi.testclient import TestClient

import main as backend_main

client = TestClient(backend_main.app)


def _register(email: str) -> None:
    res = client.post(
        "/api/auth/register",
        json={"name": "Test User", "email": email, "password": "password"},
    )
    assert res.status_code == 200, res.text


@pytest.fixture
def standard_user():
    email = f"standard-{uuid.uuid4().hex}@example.com"
    _register(email)
    return email


@pytest.fixture
def declining_user():
    email = f"fail-{uuid.uuid4().hex}@example.com"
    _register(email)
    return email


def _expected_prorated_charge(email: str) -> float:
    from datetime import datetime

    renew_at = backend_main.billing_data[email]["renew_at"]
    renew_at_date = datetime.strptime(renew_at, "%b %d, %Y")
    days_remaining = max(1, (renew_at_date - datetime.today()).days)
    daily_delta = (
        backend_main.PLANS["Premium"]["price"] - backend_main.PLANS["Standard"]["price"]
    ) / backend_main.DAYS_IN_CYCLE
    return round(daily_delta * days_remaining, 2)


# AC4 — preview contract
def test_upgrade_preview_returns_documented_contract(standard_user):
    res = client.get(f"/api/billing/upgrade-preview?email={standard_user}")
    assert res.status_code == 200
    body = res.json()
    for key in ("current_plan", "new_plan", "days_remaining", "prorated_charge", "next_renewal_price", "renew_at"):
        assert key in body
    assert body["current_plan"] == "Standard"
    assert body["new_plan"] == "Premium"
    assert body["next_renewal_price"] == 40.0
    assert body["prorated_charge"] == _expected_prorated_charge(standard_user)


# AC9 — unauthenticated
def test_upgrade_preview_unknown_email_is_401():
    res = client.get("/api/billing/upgrade-preview?email=nobody@example.com")
    assert res.status_code == 401


# AC9 — unauthenticated, POST /upgrade
def test_confirm_upgrade_unknown_email_is_401():
    res = client.post("/api/billing/upgrade", json={"email": "nobody@example.com"})
    assert res.status_code == 401


# AC5/AC6 — happy path
def test_confirm_upgrade_success_flips_plan_and_charges(standard_user):
    expected_charge = _expected_prorated_charge(standard_user)
    renew_at_before = backend_main.billing_data[standard_user]["renew_at"]

    res = client.post("/api/billing/upgrade", json={"email": standard_user})
    assert res.status_code == 200
    body = res.json()
    assert body == {"status": "success", "plan": "Premium", "charge": expected_charge}

    assert backend_main.users[standard_user]["plan"] == "Premium"
    assert backend_main.users[standard_user]["price"] == "$40/month"
    assert backend_main.billing_data[standard_user]["plan_name"] == "Premium"
    assert backend_main.billing_data[standard_user]["price"] == "$40/month"
    # renew_at preserved (AC6 / ARCH-05)
    assert backend_main.billing_data[standard_user]["renew_at"] == renew_at_before


# AC6 — Premium quotas applied
def test_confirm_upgrade_applies_premium_quotas(standard_user):
    client.post("/api/billing/upgrade", json={"email": standard_user})
    usages = {u["id"]: u for u in backend_main.billing_data[standard_user]["usages"]}
    assert usages["chat-credits"]["total"] == 10000
    assert usages["chatbots"]["total"] == 10
    assert usages["documents-pages"]["total"] == 5000
    assert backend_main.billing_data[standard_user]["on_demand_usage"]["notice"] == (
        "On-demand credit is available on your Premium plan."
    )


# AC7 — declined payment, no mutation
def test_confirm_upgrade_declined_leaves_user_on_standard(declining_user):
    res = client.post("/api/billing/upgrade", json={"email": declining_user})
    assert res.status_code == 402
    body = res.json()
    assert body["detail"] == "card_declined"
    assert body["message"] == "Your card was declined."

    assert backend_main.users[declining_user]["plan"] == "Standard"
    assert backend_main.billing_data[declining_user]["plan_name"] == "Standard"


# AC8 — already-Premium guard on both endpoints
def test_already_premium_guard_on_preview_and_upgrade(standard_user):
    client.post("/api/billing/upgrade", json={"email": standard_user})  # now Premium

    preview_res = client.get(f"/api/billing/upgrade-preview?email={standard_user}")
    assert preview_res.status_code == 409
    assert preview_res.json()["detail"] == "already_premium"

    upgrade_res = client.post("/api/billing/upgrade", json={"email": standard_user})
    assert upgrade_res.status_code == 409
    assert upgrade_res.json()["detail"] == "already_premium"


# charge_card() unit-level determinism (REQ-F-07)
def test_charge_card_is_deterministic_on_email_prefix():
    assert backend_main.charge_card("anyone@example.com", 10.0) == {"status": "success"}
    result = backend_main.charge_card("fail@example.com", 10.0)
    assert result["status"] == "card_declined"
    assert result["message"] == "Your card was declined."
