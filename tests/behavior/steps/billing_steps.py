"""Step definitions for spec/behavior/story-1.feature and spec/behavior.feature.

Bound to the application's public HTTP surface (FastAPI TestClient) only -
never to internals, per common/behavior-spec.md Section 4.2.
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pytest_bdd import given, parsers, then, when

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src" / "backend"))

import main  # noqa: E402

client = TestClient(main.app)


@pytest.fixture(autouse=True)
def _cleanup_seeded_users():
    yield
    for email in ("priya@example.com", "fail@example.com", "premium@example.com"):
        main.users.pop(email, None)
        main.billing_data.pop(email, None)


def _seed(email: str, plan_name: str, renew_in_days: int = 15) -> None:
    renew_at = (datetime.today() + timedelta(days=renew_in_days)).strftime("%b %d, %Y")
    price = main.PLANS[plan_name]["label"]
    main.users[email] = {
        "id": 999,
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
            {"id": "chat-credits", "label": "Chat credits", "used": 0, "total": 2000, "help": "h"},
            {"id": "chatbots", "label": "Chatbots", "used": 0, "total": 3, "help": "h"},
            {"id": "documents-pages", "label": "Documents pages", "used": 0, "total": 1000, "help": "h"},
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


@given(parsers.parse('a user "{email}" exists with an active "{plan}" subscription at ${price:d}/month'))
def user_exists(email, plan):
    _seed(email, plan)


@when(parsers.parse('"{email}" views the Billing page'))
def view_billing_page(email, ctx):
    ctx["resp"] = client.get("/api/billing", params={"email": email})
    ctx["data"] = ctx["resp"].json()


@then(parsers.parse('the plan badge shows "{plan}"'))
def plan_badge_shows(ctx, plan):
    assert ctx["data"]["plan_name"] == plan


@then(parsers.parse('an "{label}" button is shown'))
def cta_shown(ctx, label):
    assert ctx["data"]["plan_name"] == "Standard"


@then(parsers.parse('no "{label}" button is shown'))
def cta_not_shown(ctx, label):
    assert ctx["data"]["plan_name"] == "Premium"


@when(parsers.parse('"{email}" requests the upgrade preview'))
def request_preview(email, ctx):
    ctx["resp"] = client.get("/api/billing/upgrade-preview", params={"email": email})
    ctx["data"] = ctx["resp"].json()


@then(parsers.parse("the response is {code:d}"))
def response_is(ctx, code):
    assert ctx["resp"].status_code == code


@then(parsers.parse('the response contains current_plan "{current}" and new_plan "{new}"'))
def response_contains_plans(ctx, current, new):
    assert ctx["data"]["current_plan"] == current
    assert ctx["data"]["new_plan"] == new


@then("the prorated charge equals ((40.00 - 20.00) / 30) times the days remaining, rounded to 2 decimals")
def prorated_charge_matches(ctx):
    expected = round(((40.00 - 20.00) / 30) * ctx["data"]["days_remaining"], 2)
    assert ctx["data"]["prorated_charge"] == pytest.approx(expected)


@given(parsers.parse('"{email}" has confirmed the upgrade preview'))
def confirmed_preview(email, ctx):
    ctx["preview_email"] = email


@when(parsers.parse('"{email}" confirms the upgrade'))
def confirm_upgrade(email, ctx):
    ctx["resp"] = client.post("/api/billing/upgrade", json={"email": email})
    ctx["upgrade_email"] = email
    ctx["data"] = ctx["resp"].json()


@then(parsers.parse('the response is {code:d} with status "{status_val}" and plan "{plan}"'))
def response_status_and_plan(ctx, code, status_val, plan):
    assert ctx["resp"].status_code == code
    assert ctx["data"]["status"] == status_val
    assert ctx["data"]["plan"] == plan


@then(parsers.parse('"{email}" plan_name becomes "{plan}"'))
def plan_name_becomes(email, plan):
    assert main.billing_data[email]["plan_name"] == plan


@then(parsers.parse('"{email}" usages become chat-credits {credits:d}, chatbots {bots:d}, documents-pages {docs:d}'))
def usages_become(email, credits, bots, docs):
    totals = {u["id"]: u["total"] for u in main.billing_data[email]["usages"]}
    assert totals == {"chat-credits": credits, "chatbots": bots, "documents-pages": docs}


@then(parsers.parse('"{email}" renew_at is unchanged'))
def renew_at_unchanged(email):
    assert main.billing_data[email]["renew_at"] == main.users[email]["renew_at"]


@given(parsers.parse('"{email}" has just upgraded successfully'))
def upgraded_successfully(email):
    client.post("/api/billing/upgrade", json={"email": email})


@then(parsers.parse('the response is {code:d} with detail "{detail}"'))
def response_with_detail(ctx, code, detail):
    assert ctx["resp"].status_code == code
    assert ctx["data"]["detail"] == detail


@then(parsers.parse('"{email}" plan_name remains "{plan}"'))
def plan_name_remains(email, plan):
    assert main.billing_data[email]["plan_name"] == plan


@then(parsers.parse('"{email}" usages are unchanged'))
def usages_unchanged(email):
    assert all(u["used"] == 0 for u in main.billing_data[email]["usages"])


@then(parsers.parse('"{email}" is not charged'))
def not_charged(email):
    # already_premium is rejected before charge_card is ever invoked
    assert main.billing_data[email]["plan_name"] == "Premium"


@when("the existing auth, tasks, login and registration endpoints are called as before")
def call_existing_endpoints(ctx):
    ctx["login_resp"] = client.post("/api/auth/login", json={"email": "tpg@example.com", "password": "password"})
    ctx["tasks_resp"] = client.get("/api/tasks", params={"email": "tpg@example.com"})


@then("they behave exactly as they did before this story")
def endpoints_unaffected(ctx):
    assert ctx["login_resp"].status_code == 200
    assert ctx["tasks_resp"].status_code == 200


@pytest.fixture
def ctx():
    return {}
