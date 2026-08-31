"""pytest-bdd step definitions binding story-1.1.feature to the real application.

Bound to the actual FastAPI app through TestClient - no mock of the system under test, because the
feature file is the behaviour contract and a mock would let it pass without the contract holding.
"""

import copy
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from pytest_bdd import given, parsers, scenarios, then, when

import main

FEATURE = "../../.spec/aire-docs/implementation/code/behavior/story-1.1.feature"

scenarios(FEATURE)

SEED = "tpg@example.com"


# --------------------------------------------------------------------------- fixtures


@pytest.fixture(autouse=True)
def isolate_stores():
    users_before = copy.deepcopy(main.users)
    billing_before = copy.deepcopy(main.billing_data)
    tasks_before = copy.deepcopy(main.tasks_data)
    yield
    main.users.clear()
    main.users.update(users_before)
    main.billing_data.clear()
    main.billing_data.update(billing_before)
    main.tasks_data.clear()
    main.tasks_data.update(tasks_before)


@pytest.fixture
def ctx():
    """Scenario-scoped scratchpad: the client, the current subject, responses, snapshots."""
    return {"client": TestClient(main.app), "subject": SEED, "response": None}


def _renew_at(days_out: int) -> str:
    return (datetime.today() + timedelta(days=days_out)).strftime("%b %d, %Y")


def _seed_standard(email: str, days_out: int = 30, used=(100, 1, 15)) -> None:
    chat, bots, pages = used
    main.users[email] = {
        "id": len(main.users) + 1,
        "name": "Test",
        "email": email,
        "password": "password",
        "plan": "Standard",
        "price": "$20/month",
        "renew_at": _renew_at(days_out),
    }
    main.billing_data[email] = {
        "plan_name": "Standard",
        "price": "$20/month",
        "renew_at": _renew_at(days_out),
        "usages": [
            {"id": "chat-credits", "label": "Chat credits", "used": chat, "total": 2000,
             "help": "Messages used this billing cycle."},
            {"id": "chatbots", "label": "Chatbots", "used": bots, "total": 3,
             "help": "Active chatbot agents out of the included limit."},
            {"id": "documents-pages", "label": "Documents pages", "used": pages, "total": 1000,
             "help": f"You can add {1000 - pages} more pages of your documents."},
        ],
        "included_usage": {
            "title": "Your included usage",
            "items": [{"id": "daily", "label": "Daily quota", "used_percent": 5,
                       "resets_in": "23 hours"}],
            "help": "Usage included in your plan.",
        },
        "on_demand_usage": {
            "title": "On-demand usage",
            "remaining_balance": "$18.00",
            "your_usage": "$0.00",
            "help": "Additional usage charges beyond your included quota.",
            "notice": ("On-demand credit is not available in standard plan for usage beyond "
                       "your included quota."),
        },
    }


def _formula(days_remaining: int) -> float:
    return round((40.0 - 20.0) / 30 * days_remaining, 2)


def _usages(email: str) -> dict:
    return {u["id"]: u for u in main.billing_data[email]["usages"]}


# --------------------------------------------------------------------------- Given


@given("the billing service is running")
def service_running(ctx):
    assert ctx["client"].get("/api/billing", params={"email": SEED}).status_code == 200


@given(parsers.parse('a Standard subscriber "{email}" exists with a renewal date 30 days out'))
def standard_subscriber(ctx, email):
    _seed_standard(email, days_out=30)
    ctx["subject"] = email


@given(parsers.parse('the subscriber\'s plan is "{plan}"'))
def subscriber_plan_is(ctx, plan):
    email = ctx["subject"]
    main.billing_data[email]["plan_name"] = plan
    main.users[email]["plan"] = plan
    if plan == "Premium":
        main.billing_data[email]["price"] = "$40/month"
        main.users[email]["price"] = "$40/month"


@given(parsers.parse('a registered user "{email}" has no billing record'))
def registered_without_billing(ctx, email):
    main.users[email] = {
        "id": 999,
        "name": "Orphan",
        "email": email,
        "password": "password",
        "plan": "Standard",
        "price": "$20/month",
        "renew_at": _renew_at(30),
    }
    main.billing_data.pop(email, None)


@given("the subscriber's billing state is recorded")
def record_billing_state(ctx):
    ctx["users_snapshot"] = copy.deepcopy(main.users)
    ctx["billing_snapshot"] = copy.deepcopy(main.billing_data)


@given("the subscriber has consumed some of every quota")
def consumed_some_of_every_quota(ctx):
    for entry in main.billing_data[ctx["subject"]]["usages"]:
        assert entry["used"] > 0, "fixture must start with non-zero consumption"
    ctx["used_before"] = {u["id"]: u["used"] for u in main.billing_data[ctx["subject"]]["usages"]}
    ctx["labels_before"] = {u["id"]: u["label"] for u in main.billing_data[ctx["subject"]]["usages"]}


@given("the subscriber's renewal date is recorded from both stores")
def record_renewal_dates(ctx):
    email = ctx["subject"]
    ctx["user_renew"] = main.users[email]["renew_at"]
    ctx["billing_renew"] = main.billing_data[email]["renew_at"]


# --------------------------------------------------------------------------- When


@when("the subscriber fetches their billing data")
def fetch_billing(ctx):
    ctx["response"] = ctx["client"].get("/api/billing", params={"email": ctx["subject"]})


@when(parsers.parse('"{email}" fetches their billing data'))
def fetch_billing_as(ctx, email):
    ctx["response"] = ctx["client"].get("/api/billing", params={"email": email})


@when("the subscriber requests an upgrade preview")
def request_preview(ctx):
    ctx["response"] = ctx["client"].get(
        "/api/billing/upgrade-preview", params={"email": ctx["subject"]}
    )


@when(parsers.parse('an unknown caller "{email}" requests an upgrade preview'))
@when(parsers.parse('"{email}" requests an upgrade preview'))
def request_preview_as(ctx, email):
    ctx["response"] = ctx["client"].get("/api/billing/upgrade-preview", params={"email": email})


@when("the subscriber confirms the upgrade")
def confirm_upgrade(ctx):
    email = ctx["subject"]
    preview = ctx["client"].get("/api/billing/upgrade-preview", params={"email": email})
    if preview.status_code == 200:
        ctx["days_remaining"] = preview.json()["days_remaining"]
    ctx["response"] = ctx["client"].post("/api/billing/upgrade", json={"email": email})


@when(parsers.parse('"{email}" confirms the upgrade'))
def confirm_upgrade_as(ctx, email):
    ctx["subject"] = email
    preview = ctx["client"].get("/api/billing/upgrade-preview", params={"email": email})
    if preview.status_code == 200:
        ctx["days_remaining"] = preview.json()["days_remaining"]
    ctx["response"] = ctx["client"].post("/api/billing/upgrade", json={"email": email})


@when(parsers.parse("the subscriber confirms the upgrade while supplying their own amount of {amount}"))
def confirm_upgrade_with_amount(ctx, amount):
    amount = float(amount)
    email = ctx["subject"]
    preview = ctx["client"].get("/api/billing/upgrade-preview", params={"email": email})
    if preview.status_code == 200:
        ctx["days_remaining"] = preview.json()["days_remaining"]
    ctx["injected_amount"] = amount
    ctx["response"] = ctx["client"].post(
        "/api/billing/upgrade", json={"email": email, "amount": amount}
    )


@when(parsers.parse('the gateway is asked to charge "{email}"'))
def gateway_charge(ctx, email):
    ctx["gateway_result"] = main.charge_card(email, 19.33)


# --------------------------------------------------------------------------- Then


@then("the request succeeds")
def request_succeeds(ctx):
    assert ctx["response"].status_code == 200, ctx["response"].text


@then("the request is rejected as unauthenticated")
def rejected_unauthenticated(ctx):
    assert ctx["response"].status_code == 401


@then("the request is rejected because the billing record was not found")
def rejected_not_found(ctx):
    assert ctx["response"].status_code == 404
    assert ctx["response"].json() == {"detail": "billing_record_not_found"}


@then("the request is rejected as already premium")
def rejected_already_premium(ctx):
    assert ctx["response"].status_code == 409
    assert ctx["response"].json() == {"detail": "already_premium"}


@then("the request is rejected as payment required")
def rejected_payment_required(ctx):
    assert ctx["response"].status_code == 402


@then(parsers.parse('the response does not contain any data belonging to "{email}"'))
def no_other_user_data(ctx, email):
    assert email not in ctx["response"].text


@then(parsers.parse('the response plan name is "{plan}"'))
def response_plan_name(ctx, plan):
    assert ctx["response"].json()["plan_name"] == plan


@then(parsers.parse('the response price is "{price}"'))
def response_price(ctx, price):
    assert ctx["response"].json()["price"] == price


@then(parsers.parse('the plan name in the response is "{plan}"'))
def plan_name_in_response(ctx, plan):
    assert ctx["response"].json()["plan_name"] == plan


@then(parsers.parse("an upgrade is {eligibility} for that plan"))
def upgrade_eligibility(ctx, eligibility):
    plan = ctx["response"].json()["plan_name"]
    offered = plan == "Standard"
    expected = eligibility.strip() == "offered"
    assert offered is expected

    # The API must agree with what the UI would render from the same payload.
    preview = ctx["client"].get(
        "/api/billing/upgrade-preview", params={"email": ctx["subject"]}
    )
    assert (preview.status_code == 200) is expected


@then(parsers.parse('the quote names the current plan "{current}" and the new plan "{new}"'))
def quote_names_plans(ctx, current, new):
    body = ctx["response"].json()
    assert body["current_plan"] == current
    assert body["new_plan"] == new


@then(parsers.parse("the quote's next renewal price is {price}"))
def quote_next_price(ctx, price):
    assert ctx["response"].json()["next_renewal_price"] == float(price)


@then("the quote echoes the stored renewal date unchanged")
def quote_echoes_renew_at(ctx):
    assert ctx["response"].json()["renew_at"] == main.billing_data[ctx["subject"]]["renew_at"]


@then("the quote's prorated charge equals the proration formula for its own days remaining")
def quote_matches_formula(ctx):
    body = ctx["response"].json()
    assert body["prorated_charge"] == _formula(body["days_remaining"])


@then(parsers.parse("the quote's days remaining is at least {n:d}"))
def days_at_least(ctx, n):
    assert ctx["response"].json()["days_remaining"] >= n


@then(parsers.parse("the quote's days remaining is at most {n:d}"))
def days_at_most(ctx, n):
    assert ctx["response"].json()["days_remaining"] <= n


@then(parsers.parse("the quote's prorated charge is greater than {n}"))
def charge_greater_than(ctx, n):
    assert ctx["response"].json()["prorated_charge"] > float(n)


@then(parsers.parse("the quote's prorated charge is at most {n}"))
def charge_at_most(ctx, n):
    assert ctx["response"].json()["prorated_charge"] <= float(n)


@then(parsers.parse('the gateway result is "{result}"'))
def gateway_result_is(ctx, result):
    assert ctx["gateway_result"]["status"] == result


@then(parsers.parse('the response reports the plan "{plan}"'))
def response_reports_plan(ctx, plan):
    assert ctx["response"].json()["plan"] == plan


@then("the response's charge equals the proration formula for the days that remained")
def response_charge_matches_formula(ctx):
    assert ctx["response"].json()["charge"] == _formula(ctx["days_remaining"])


@then(parsers.parse("the response's charge is not {n}"))
def response_charge_is_not(ctx, n):
    assert ctx["response"].json()["charge"] != float(n)


@then(parsers.parse('the user record shows the plan "{plan}" priced "{price}"'))
def user_record_shows(ctx, plan, price):
    assert main.users[ctx["subject"]]["plan"] == plan
    assert main.users[ctx["subject"]]["price"] == price


@then(parsers.parse('the billing record shows the plan "{plan}" priced "{price}"'))
def billing_record_shows(ctx, plan, price):
    assert main.billing_data[ctx["subject"]]["plan_name"] == plan
    assert main.billing_data[ctx["subject"]]["price"] == price


@then(parsers.parse("the chat credits total is {n:d}"))
def chat_credits_total(ctx, n):
    email = ctx["subject"]
    if ctx["response"] is not None and ctx["response"].status_code == 200 and \
            "usages" in ctx["response"].text:
        body = {u["id"]: u for u in ctx["response"].json()["usages"]}
        assert body["chat-credits"]["total"] == n
    else:
        assert _usages(email)["chat-credits"]["total"] == n


@then(parsers.parse("the chatbots total is {n:d}"))
def chatbots_total(ctx, n):
    email = ctx["subject"]
    if ctx["response"] is not None and ctx["response"].status_code == 200 and \
            "usages" in ctx["response"].text:
        body = {u["id"]: u for u in ctx["response"].json()["usages"]}
        assert body["chatbots"]["total"] == n
    else:
        assert _usages(email)["chatbots"]["total"] == n


@then(parsers.parse("the document pages total is {n:d}"))
def document_pages_total(ctx, n):
    email = ctx["subject"]
    if ctx["response"] is not None and ctx["response"].status_code == 200 and \
            "usages" in ctx["response"].text:
        body = {u["id"]: u for u in ctx["response"].json()["usages"]}
        assert body["documents-pages"]["total"] == n
    else:
        assert _usages(email)["documents-pages"]["total"] == n


@then("every quota's consumed amount is unchanged")
def consumed_unchanged(ctx):
    after = {u["id"]: u["used"] for u in main.billing_data[ctx["subject"]]["usages"]}
    assert after == ctx["used_before"]


@then("every quota keeps its original id and label")
def labels_unchanged(ctx):
    after = {u["id"]: u["label"] for u in main.billing_data[ctx["subject"]]["usages"]}
    assert after == ctx["labels_before"]


@then(parsers.parse('the on-demand notice reads "{notice}"'))
def notice_reads(ctx, notice):
    assert main.billing_data[ctx["subject"]]["on_demand_usage"]["notice"] == notice


@then("the renewal date in the user record is unchanged")
def user_renew_unchanged(ctx):
    assert main.users[ctx["subject"]]["renew_at"] == ctx["user_renew"]


@then("the renewal date in the billing record is unchanged")
def billing_renew_unchanged(ctx):
    assert main.billing_data[ctx["subject"]]["renew_at"] == ctx["billing_renew"]


@then(parsers.parse('an upgrade is not offered for that plan'))
def upgrade_not_offered(ctx):
    assert ctx["response"].json()["plan_name"] == "Premium"
    preview = ctx["client"].get(
        "/api/billing/upgrade-preview", params={"email": ctx["subject"]}
    )
    assert preview.status_code == 409


@then(parsers.parse('the error detail is "{detail}"'))
def error_detail_is(ctx, detail):
    assert ctx["response"].json()["detail"] == detail


@then(parsers.parse('the error message is "{message}"'))
def error_message_is(ctx, message):
    assert ctx["response"].json()["message"] == message


@then("the error body contains no other fields")
def error_body_exact(ctx):
    assert set(ctx["response"].json()) == {"detail", "message"}


@then("the subscriber's billing state is completely unchanged")
def billing_state_unchanged(ctx):
    assert main.users == ctx["users_snapshot"]
    assert main.billing_data == ctx["billing_snapshot"]
