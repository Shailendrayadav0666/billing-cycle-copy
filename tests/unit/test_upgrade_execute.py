"""POST /api/billing/upgrade, happy path — FR-7, FR-11, FR-13, AC-19..AC-23, AC-27, AC-28."""

import main
from conftest import expected_charge


def _upgrade(client, email, **extra):
    return client.post("/api/billing/upgrade", json={"email": email, **extra})


def test_response_reports_success_the_new_plan_and_the_charge(client, make_subscriber):
    """AC-19."""
    email = make_subscriber("u1@example.com", days_out=30)
    preview = client.get("/api/billing/upgrade-preview", params={"email": email}).json()

    res = _upgrade(client, email)

    assert res.status_code == 200
    body = res.json()
    assert body == {"status": "success", "plan": "Premium", "charge": preview["prorated_charge"]}
    assert body["charge"] == expected_charge(preview["days_remaining"])


def test_both_stores_are_flipped_to_premium(client, make_subscriber):
    """AC-20."""
    email = make_subscriber("u2@example.com", days_out=30)
    _upgrade(client, email)

    assert main.users[email]["plan"] == "Premium"
    assert main.users[email]["price"] == "$40/month"
    assert main.billing_data[email]["plan_name"] == "Premium"
    assert main.billing_data[email]["price"] == "$40/month"


def test_quota_ceilings_rise_and_consumption_is_preserved(client, make_subscriber):
    """AC-21."""
    email = make_subscriber("u3@example.com", days_out=30, used=(100, 1, 15))
    _upgrade(client, email)

    usages = {u["id"]: u for u in main.billing_data[email]["usages"]}
    assert usages["chat-credits"]["total"] == 10000
    assert usages["chatbots"]["total"] == 10
    assert usages["documents-pages"]["total"] == 5000
    assert usages["chat-credits"]["used"] == 100
    assert usages["chatbots"]["used"] == 1
    assert usages["documents-pages"]["used"] == 15
    assert usages["chat-credits"]["label"] == "Chat credits"


def test_the_on_demand_notice_is_replaced(client, make_subscriber):
    """AC-22."""
    email = make_subscriber("u4@example.com", days_out=30)
    _upgrade(client, email)

    notice = main.billing_data[email]["on_demand_usage"]["notice"]
    assert notice == "On-demand credit is available on your Premium plan."
    assert "not available" not in notice


def test_the_renewal_date_is_unchanged_in_both_stores(client, make_subscriber):
    """AC-23 / FR-11. Both copies are checked, because they are written independently."""
    email = make_subscriber("u5@example.com", days_out=30)
    user_renew_before = main.users[email]["renew_at"]
    billing_renew_before = main.billing_data[email]["renew_at"]

    _upgrade(client, email)

    assert main.users[email]["renew_at"] == user_renew_before
    assert main.billing_data[email]["renew_at"] == billing_renew_before


def test_untouched_fields_stay_untouched(client, make_subscriber):
    """The Epic changes only the notice, so the balance figures must not move."""
    email = make_subscriber("u6@example.com", days_out=30)
    od_before = dict(main.billing_data[email]["on_demand_usage"])
    included_before = main.billing_data[email]["included_usage"]

    _upgrade(client, email)

    od_after = main.billing_data[email]["on_demand_usage"]
    assert od_after["remaining_balance"] == od_before["remaining_balance"]
    assert od_after["your_usage"] == od_before["your_usage"]
    assert od_after["title"] == od_before["title"]
    assert main.billing_data[email]["included_usage"] == included_before


def test_identity_fields_are_never_written(client, make_subscriber):
    email = make_subscriber("u7@example.com", days_out=30)
    before = {k: main.users[email][k] for k in ("id", "name", "email", "password")}

    _upgrade(client, email)

    for key, value in before.items():
        assert main.users[email][key] == value


def test_a_later_billing_fetch_reports_premium(client, make_subscriber):
    """AC-27 / AC-28: the state is served by the API, not held only in UI state."""
    email = make_subscriber("u8@example.com", days_out=30)
    _upgrade(client, email)

    body = client.get("/api/billing", params={"email": email}).json()
    assert body["plan_name"] == "Premium"
    assert body["price"] == "$40/month"
    usages = {u["id"]: u for u in body["usages"]}
    assert usages["chat-credits"]["total"] == 10000


def test_upgrading_twice_is_refused_so_a_double_charge_is_impossible(client, make_subscriber):
    """AC-11: idempotent by guard rather than by nature."""
    email = make_subscriber("u9@example.com", days_out=30)

    assert _upgrade(client, email).status_code == 200
    second = _upgrade(client, email)

    assert second.status_code == 409
    assert second.json() == {"detail": "already_premium"}


def test_an_unknown_caller_cannot_upgrade(client):
    res = _upgrade(client, "nobody@example.com")
    assert res.status_code == 401


def test_a_caller_with_no_billing_record_cannot_upgrade_another_users_record(client, make_subscriber):
    """SEC-2: the seed user must not be mutated on behalf of an orphaned account."""
    email = make_subscriber("u10@example.com", days_out=30)
    main.billing_data.pop(email)
    seed_plan_before = main.billing_data["tpg@example.com"]["plan_name"]

    res = _upgrade(client, email)

    assert res.status_code == 404
    assert main.billing_data["tpg@example.com"]["plan_name"] == seed_plan_before


def test_a_premium_caller_changes_nothing(client, make_subscriber):
    """AC-11."""
    email = make_subscriber("u11@example.com", days_out=30)
    main.billing_data[email]["plan_name"] = "Premium"
    usages_before = [dict(u) for u in main.billing_data[email]["usages"]]

    res = _upgrade(client, email)

    assert res.status_code == 409
    assert main.billing_data[email]["usages"] == usages_before
    assert main.users[email]["plan"] == "Standard"


def test_only_the_six_expected_fields_are_written(client, make_subscriber):
    """Pins the Zone C write set, so a later edit cannot quietly widen it."""
    email = make_subscriber("u12@example.com", days_out=30)
    import copy

    users_before = copy.deepcopy(main.users[email])
    billing_before = copy.deepcopy(main.billing_data[email])

    _upgrade(client, email)

    changed_user = {
        k for k in users_before if users_before[k] != main.users[email][k]
    }
    changed_billing = {
        k for k in billing_before if billing_before[k] != main.billing_data[email][k]
    }

    assert changed_user == {"plan", "price"}
    assert changed_billing == {"plan_name", "price", "usages", "on_demand_usage"}
