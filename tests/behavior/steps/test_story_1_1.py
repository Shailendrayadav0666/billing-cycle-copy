"""Step definitions for spec/behavior/story-1.1.feature — bound to the FastAPI public surface
(the same HTTP endpoints the frontend calls), never to internals, per common/behavior-spec.md."""
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src" / "backend"))

from fastapi.testclient import TestClient
from pytest_bdd import given, parsers, scenarios, then, when

import main as backend_main

scenarios("../../../spec/behavior/story-1.1.feature")

client = TestClient(backend_main.app)


@given(parsers.parse('a Standard subscriber "{email_hint}" with 15 days remaining in the billing cycle'))
def standard_subscriber_15_days(context, email_hint):
    email = f"{email_hint.split('@')[0]}-{uuid.uuid4().hex}@example.com"
    client.post("/api/auth/register", json={"name": "Subscriber", "email": email, "password": "password"})
    renew_at = (datetime.today() + timedelta(days=15)).strftime("%b %d, %Y")
    backend_main.users[email]["renew_at"] = renew_at
    backend_main.billing_data[email]["renew_at"] = renew_at
    context["email"] = email
    context["renew_at_before"] = renew_at


@given(parsers.parse('a Premium subscriber "{email_hint}"'))
def premium_subscriber(context, email_hint):
    email = f"{email_hint.split('@')[0]}-{uuid.uuid4().hex}@example.com"
    client.post("/api/auth/register", json={"name": "Subscriber", "email": email, "password": "password"})
    backend_main.users[email]["plan"] = "Premium"
    backend_main.billing_data[email]["plan_name"] = "Premium"
    context["email"] = email


@given(parsers.parse('the subscriber\'s email does not start with "{prefix}"'))
def email_does_not_start_with(context, prefix):
    assert not context["email"].startswith(prefix)


@given(parsers.parse('the subscriber\'s email starts with "{prefix}"'))
def make_email_start_with(context, prefix):
    old_email = context["email"]
    new_email = f"{prefix}-{uuid.uuid4().hex}@example.com"
    backend_main.users[new_email] = {**backend_main.users[old_email], "email": new_email}
    backend_main.billing_data[new_email] = backend_main.billing_data[old_email]
    context["email"] = new_email


@when("the subscriber views the Billing page")
def view_billing_page(context):
    context["billing_response"] = client.get(f"/api/billing?email={context['email']}")


@when("the subscriber requests the upgrade preview")
def request_preview(context):
    context["response"] = client.get(f"/api/billing/upgrade-preview?email={context['email']}")


@when(parsers.parse('the subscriber requests "GET /api/billing/upgrade-preview"'))
def request_preview_contract(context):
    context["response"] = client.get(f"/api/billing/upgrade-preview?email={context['email']}")


@when("the subscriber confirms the upgrade")
def confirm_upgrade(context):
    context["response"] = client.post("/api/billing/upgrade", json={"email": context["email"]})


@when("an unknown email requests the upgrade preview")
def unknown_email_preview(context):
    context["response"] = client.get("/api/billing/upgrade-preview?email=nobody@example.com")


@then('an "Upgrade to Premium" action is available')
def upgrade_action_available(context):
    body = context["billing_response"].json()
    assert body["plan_name"] == "Standard"


@then(parsers.parse('the plan badge shows "{plan}"'))
def plan_badge_shows(context, plan):
    assert context["billing_response"].json()["plan_name"] == plan


@then(parsers.parse('the plan price shows "{price}"'))
def plan_price_shows(context, price):
    assert context["billing_response"].json()["price"] == price


@then(parsers.parse('the preview shows current plan "{current}" and new plan "{new}"'))
def preview_shows_plans(context, current, new):
    body = context["response"].json()
    assert body["current_plan"] == current
    assert body["new_plan"] == new


@then("the preview shows the prorated charge computed from the proration formula")
def preview_shows_computed_charge(context):
    email = context["email"]
    renew_at_date = datetime.strptime(backend_main.billing_data[email]["renew_at"], "%b %d, %Y")
    days_remaining = max(1, (renew_at_date - datetime.today()).days)
    daily_delta = (backend_main.PLANS["Premium"]["price"] - backend_main.PLANS["Standard"]["price"]) / backend_main.DAYS_IN_CYCLE
    expected = round(daily_delta * days_remaining, 2)
    assert context["response"].json()["prorated_charge"] == expected


@then(parsers.parse('the preview shows the next renewal price of "{amount}"'))
def preview_shows_renewal_price(context, amount):
    assert context["response"].json()["next_renewal_price"] == float(amount)


@then("the response contains current_plan, new_plan, days_remaining, prorated_charge, next_renewal_price, renew_at")
def response_contains_contract(context):
    body = context["response"].json()
    for key in ("current_plan", "new_plan", "days_remaining", "prorated_charge", "next_renewal_price", "renew_at"):
        assert key in body


@then("the payment gateway is charged the prorated amount")
def gateway_charged(context):
    assert context["response"].status_code == 200
    assert context["response"].json()["charge"] > 0


@then(parsers.parse('the response reports status "{status_value}" and plan "{plan}"'))
def response_reports_status_and_plan(context, status_value, plan):
    body = context["response"].json()
    assert body["status"] == status_value
    assert body["plan"] == plan


@then(parsers.parse('the plan becomes "{plan}" with price "{price}"'))
def plan_becomes(context, plan, price):
    assert backend_main.users[context["email"]]["plan"] == plan
    assert backend_main.billing_data[context["email"]]["price"] == price


@then(parsers.parse("the chat credits quota becomes {total:d}"))
def chat_credits_quota(context, total):
    usages = {u["id"]: u for u in backend_main.billing_data[context["email"]]["usages"]}
    assert usages["chat-credits"]["total"] == total


@then(parsers.parse("the chatbots quota becomes {total:d}"))
def chatbots_quota(context, total):
    usages = {u["id"]: u for u in backend_main.billing_data[context["email"]]["usages"]}
    assert usages["chatbots"]["total"] == total


@then(parsers.parse("the documents pages quota becomes {total:d}"))
def documents_pages_quota(context, total):
    usages = {u["id"]: u for u in backend_main.billing_data[context["email"]]["usages"]}
    assert usages["documents-pages"]["total"] == total


@then("the renew_at date is unchanged")
def renew_at_unchanged(context):
    assert backend_main.billing_data[context["email"]]["renew_at"] == context["renew_at_before"]


@then(parsers.parse("the response status code is {code:d}"))
def response_status_code(context, code):
    assert context["response"].status_code == code


@then(parsers.parse('the response detail is "{detail}"'))
def response_detail_is(context, detail):
    assert context["response"].json()["detail"] == detail


@then(parsers.parse('the subscriber\'s plan is still "{plan}"'))
def subscriber_plan_is_still(context, plan):
    assert backend_main.users[context["email"]]["plan"] == plan
