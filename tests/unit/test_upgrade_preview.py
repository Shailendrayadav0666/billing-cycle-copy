"""GET /api/billing/upgrade-preview — FR-4, FR-9, SEC-1, SEC-2, AC-5, AC-8, AC-9, AC-10."""

import copy

import main
from conftest import SEED_EMAIL, expected_charge


def _preview(client, email):
    return client.get("/api/billing/upgrade-preview", params={"email": email})


def test_returns_the_complete_quote_shape(client, make_subscriber):
    email = make_subscriber("p1@example.com", days_out=30)
    res = _preview(client, email)

    assert res.status_code == 200
    body = res.json()
    assert set(body) == {
        "current_plan",
        "new_plan",
        "days_remaining",
        "prorated_charge",
        "next_renewal_price",
        "renew_at",
    }
    assert body["current_plan"] == "Standard"
    assert body["new_plan"] == "Premium"
    assert body["next_renewal_price"] == 40.0


def test_the_quoted_charge_matches_the_formula_for_its_own_days_remaining(client, make_subscriber):
    email = make_subscriber("p2@example.com", days_out=30)
    body = _preview(client, email).json()
    assert body["prorated_charge"] == expected_charge(body["days_remaining"])


def test_it_echoes_the_stored_renewal_date_unchanged(client, make_subscriber):
    email = make_subscriber("p3@example.com", days_out=30)
    body = _preview(client, email).json()
    assert body["renew_at"] == main.billing_data[email]["renew_at"]


def test_it_writes_nothing(client, make_subscriber):
    """The preview is read-only, so it is safe to call on every click of the CTA."""
    email = make_subscriber("p4@example.com", days_out=30)
    users_before = copy.deepcopy(main.users)
    billing_before = copy.deepcopy(main.billing_data)

    _preview(client, email)
    _preview(client, email)

    assert main.users == users_before
    assert main.billing_data == billing_before


def test_repeated_calls_are_identical(client, make_subscriber):
    email = make_subscriber("p5@example.com", days_out=30)
    assert _preview(client, email).json() == _preview(client, email).json()


def test_an_unknown_caller_is_rejected_as_unauthenticated(client):
    """SEC-1 / AC-8: authentication is checked first, matching the existing endpoints."""
    res = _preview(client, "nobody@example.com")
    assert res.status_code == 401
    assert res.json() == {"detail": "Not authenticated"}


def test_a_caller_with_no_billing_record_gets_404_not_another_users_data(client):
    """SEC-2 / AC-9: the seed-user fallback used by GET /api/billing is NOT reproduced here.

    This is the test that pins finding F-3. Without it, an orphaned user would be quoted - and
    later charged - against tpg@example.com's billing record.
    """
    main.users["orphan@example.com"] = {
        "id": 99,
        "name": "Orphan",
        "email": "orphan@example.com",
        "password": "password",
        "plan": "Standard",
        "price": "$20/month",
        "renew_at": main.billing_data[SEED_EMAIL]["renew_at"],
    }
    main.billing_data.pop("orphan@example.com", None)

    res = _preview(client, "orphan@example.com")

    assert res.status_code == 404
    assert res.json() == {"detail": "billing_record_not_found"}
    assert SEED_EMAIL not in res.text


def test_a_premium_subscriber_cannot_preview(client, make_subscriber):
    """AC-10."""
    email = make_subscriber("p6@example.com", days_out=30)
    main.billing_data[email]["plan_name"] = "Premium"

    res = _preview(client, email)

    assert res.status_code == 409
    assert res.json() == {"detail": "already_premium"}


def test_an_unrecognised_plan_is_refused_rather_than_upgraded(client, make_subscriber):
    """BR-1 uses strict equality, so an unexpected plan value is not silently treated as eligible."""
    email = make_subscriber("p7@example.com", days_out=30)
    main.billing_data[email]["plan_name"] = "Enterprise"

    res = _preview(client, email)

    assert res.status_code == 409


def test_the_guard_order_does_not_leak_existence_before_authentication(client, make_subscriber):
    """SEC-1: an unauthenticated caller learns nothing about plan or billing state."""
    email = make_subscriber("p8@example.com", days_out=30)
    main.billing_data[email]["plan_name"] = "Premium"
    main.users.pop(email)

    res = _preview(client, email)

    # 401, not 409 - the caller is not told the account is already Premium.
    assert res.status_code == 401
