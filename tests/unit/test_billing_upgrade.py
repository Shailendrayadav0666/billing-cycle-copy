"""Unit tests for Story 1 - Mid-Cycle Subscription Upgrade (Standard -> Premium).

Covers: charge_card(), _compute_prorated_charge(), and the two new endpoints
GET /api/billing/upgrade-preview and POST /api/billing/upgrade.
Traces to spec/plans/stories.md Story 1 AC-1..AC-9 / spec/plans/requirements.md REQ-F-*/REQ-NF-*.
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src" / "backend"))

import main  # noqa: E402

client = TestClient(main.app)


def _seed_user(email: str, plan_name: str = "Standard", renew_in_days: int = 15) -> None:
    renew_at = (datetime.today() + timedelta(days=renew_in_days)).strftime("%b %d, %Y")
    price = main.PLANS[plan_name]["label"]
    main.users[email] = {
        "id": len(main.users) + 1,
        "name": email,
        "email": email,
        "password": "password",
        "plan": plan_name,
        "price": price,
        "renew_at": renew_at,
    }
    usages = (
        [dict(u) for u in main.PREMIUM_QUOTAS["usages"]]
        if plan_name == "Premium"
        else [
            {"id": "chat-credits", "label": "Chat credits", "used": 100, "total": 2000, "help": "h"},
            {"id": "chatbots", "label": "Chatbots", "used": 1, "total": 3, "help": "h"},
            {"id": "documents-pages", "label": "Documents pages", "used": 15, "total": 1000, "help": "h"},
        ]
    )
    main.billing_data[email] = {
        "plan_name": plan_name,
        "price": price,
        "renew_at": renew_at,
        "usages": usages,
        "included_usage": {"title": "t", "items": []},
        "on_demand_usage": {
            "title": "t",
            "remaining_balance": "$0.00",
            "your_usage": "$0.00",
            "help": "h",
            "notice": "On-demand credit is not available in standard plan for usage beyond your included quota.",
        },
    }


@pytest.fixture(autouse=True)
def _cleanup():
    yield
    for email in ("priya@example.com", "fail@example.com", "premium@example.com"):
        main.users.pop(email, None)
        main.billing_data.pop(email, None)


# --- charge_card() (REQ-F-09, REQ-NF-02, REQ-NF-03, ARCH-02) -------------------------------


def test_charge_card_succeeds_for_normal_email():
    assert main.charge_card("priya@example.com", 10.0) == {"status": "success"}


def test_charge_card_declines_for_fail_prefixed_email():
    result = main.charge_card("fail@example.com", 10.0)
    assert result["status"] == "card_declined"
    assert result["message"] == "Your card was declined."


def test_charge_card_is_deterministic():
    assert main.charge_card("fail-x@example.com", 5.0)["status"] == "card_declined"
    assert main.charge_card("fail-x@example.com", 5.0)["status"] == "card_declined"


# --- _compute_prorated_charge() (REQ-F-08, ARCH-01) ----------------------------------------


def test_prorated_charge_matches_epic_example():
    renew_at = (datetime.today() + timedelta(days=15)).strftime("%b %d, %Y")
    days_remaining, charge = main._compute_prorated_charge(renew_at)
    assert days_remaining == 15
    assert charge == pytest.approx(10.00)


def test_prorated_charge_floors_at_one_day():
    renew_at = datetime.today().strftime("%b %d, %Y")
    days_remaining, _charge = main._compute_prorated_charge(renew_at)
    assert days_remaining >= 1


# --- GET /api/billing/upgrade-preview (AC-2, AC-3, AC-8) -----------------------------------


def test_upgrade_preview_returns_server_computed_values():
    _seed_user("priya@example.com", "Standard", renew_in_days=15)
    resp = client.get("/api/billing/upgrade-preview", params={"email": "priya@example.com"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["current_plan"] == "Standard"
    assert body["new_plan"] == "Premium"
    assert body["days_remaining"] == 15
    assert body["prorated_charge"] == pytest.approx(10.00)
    assert body["next_renewal_price"] == 40.0


def test_upgrade_preview_already_premium_returns_409():
    _seed_user("premium@example.com", "Premium")
    resp = client.get("/api/billing/upgrade-preview", params={"email": "premium@example.com"})
    assert resp.status_code == 409
    assert resp.json()["detail"] == "already_premium"


def test_upgrade_preview_unauthenticated_returns_401():
    resp = client.get("/api/billing/upgrade-preview", params={"email": "nobody@example.com"})
    assert resp.status_code == 401


# --- POST /api/billing/upgrade (AC-5, AC-7, AC-8) ------------------------------------------


def test_upgrade_success_flips_plan_and_quotas():
    _seed_user("priya@example.com", "Standard", renew_in_days=15)
    original_renew_at = main.billing_data["priya@example.com"]["renew_at"]

    resp = client.post("/api/billing/upgrade", json={"email": "priya@example.com"})

    assert resp.status_code == 200
    body = resp.json()
    assert body == {"status": "success", "plan": "Premium", "charge": pytest.approx(10.00)}
    assert main.users["priya@example.com"]["plan"] == "Premium"
    assert main.users["priya@example.com"]["price"] == "$40/month"
    account = main.billing_data["priya@example.com"]
    assert account["plan_name"] == "Premium"
    assert account["price"] == "$40/month"
    totals = {u["id"]: u["total"] for u in account["usages"]}
    assert totals == {"chat-credits": 10000, "chatbots": 10, "documents-pages": 5000}
    assert all(u["used"] == 0 for u in account["usages"])
    assert account["on_demand_usage"]["notice"] == "On-demand credit is available on your Premium plan."
    assert account["renew_at"] == original_renew_at


def test_upgrade_declined_mutates_nothing_and_returns_402():
    _seed_user("fail@example.com", "Standard", renew_in_days=15)
    before = dict(main.billing_data["fail@example.com"])

    resp = client.post("/api/billing/upgrade", json={"email": "fail@example.com"})

    assert resp.status_code == 402
    body = resp.json()
    assert body["detail"] == "card_declined"
    assert body["message"] == "Your card was declined."
    assert main.users["fail@example.com"]["plan"] == "Standard"
    assert main.billing_data["fail@example.com"] == before


def test_upgrade_already_premium_returns_409_and_does_not_charge():
    _seed_user("premium@example.com", "Premium")
    before = dict(main.billing_data["premium@example.com"])

    resp = client.post("/api/billing/upgrade", json={"email": "premium@example.com"})

    assert resp.status_code == 409
    assert resp.json()["detail"] == "already_premium"
    assert main.billing_data["premium@example.com"] == before


def test_upgrade_unauthenticated_returns_401():
    resp = client.post("/api/billing/upgrade", json={"email": "nobody@example.com"})
    assert resp.status_code == 401


# --- Scope guardrail (AC-9, REQ-F-18) ------------------------------------------------------


def test_existing_endpoints_unaffected():
    resp = client.post("/api/auth/login", json={"email": "tpg@example.com", "password": "password"})
    assert resp.status_code == 200
    resp = client.get("/api/tasks", params={"email": "tpg@example.com"})
    assert resp.status_code == 200
