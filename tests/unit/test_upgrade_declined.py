"""POST /api/billing/upgrade, declined path — FR-8, NFR-5, SEC-5, AC-24, AC-25, AC-26, AC-31.

The central assertion here is that a declined card mutates absolutely nothing. It is checked by
deep-comparing a full snapshot of both stores taken before the request, rather than by spot-checking
individual fields, so a write to any field at all fails the test.
"""

import copy

import main


def _upgrade(client, email):
    return client.post("/api/billing/upgrade", json={"email": email})


def test_a_declined_card_returns_402(client, make_subscriber):
    """AC-24."""
    email = make_subscriber("fail1@example.com", days_out=30)
    res = _upgrade(client, email)
    assert res.status_code == 402


def test_the_402_body_is_the_exact_contract_shape(client, make_subscriber):
    """AC-24 / AC-26: exactly two keys, both fixed literals."""
    email = make_subscriber("fail2@example.com", days_out=30)
    body = _upgrade(client, email).json()

    assert body == {"detail": "card_declined", "message": "Your card was declined."}


def test_the_error_body_discloses_nothing_internal(client, make_subscriber):
    """SEC-5 / AC-26: no stack trace, no dict contents, no other user's data."""
    email = make_subscriber("fail3@example.com", days_out=30)
    text = _upgrade(client, email).text

    for leak in ("tpg@example.com", "password", "Traceback", "billing_data", "users[", "renew_at"):
        assert leak not in text


def test_a_declined_card_mutates_absolutely_nothing(client, make_subscriber):
    """AC-25 / NFR-5. The whole-store deep compare is the point of this test."""
    email = make_subscriber("fail4@example.com", days_out=30)

    users_snapshot = copy.deepcopy(main.users)
    billing_snapshot = copy.deepcopy(main.billing_data)
    tasks_snapshot = copy.deepcopy(main.tasks_data)

    res = _upgrade(client, email)

    assert res.status_code == 402
    assert main.users == users_snapshot
    assert main.billing_data == billing_snapshot
    assert main.tasks_data == tasks_snapshot


def test_the_subscriber_remains_on_standard_with_standard_quotas(client, make_subscriber):
    """AC-31."""
    email = make_subscriber("fail5@example.com", days_out=30)
    _upgrade(client, email)

    body = client.get("/api/billing", params={"email": email}).json()
    assert body["plan_name"] == "Standard"
    assert body["price"] == "$20/month"
    usages = {u["id"]: u for u in body["usages"]}
    assert usages["chat-credits"]["total"] == 2000
    assert usages["chatbots"]["total"] == 3
    assert usages["documents-pages"]["total"] == 1000


def test_the_standard_on_demand_notice_survives_a_decline(client, make_subscriber):
    email = make_subscriber("fail6@example.com", days_out=30)
    _upgrade(client, email)

    notice = main.billing_data[email]["on_demand_usage"]["notice"]
    assert "not available in standard plan" in notice


def test_a_declined_attempt_can_be_retried_after_the_cause_is_fixed(client, make_subscriber):
    """A failed attempt must leave no residue that blocks a later legitimate upgrade."""
    email = make_subscriber("fail7@example.com", days_out=30)

    assert _upgrade(client, email).status_code == 402
    assert _upgrade(client, email).status_code == 402

    # Same account, now resolvable by the gateway - simulates the card being fixed.
    main.users["ok7@example.com"] = dict(main.users[email], email="ok7@example.com")
    main.billing_data["ok7@example.com"] = copy.deepcopy(main.billing_data[email])

    assert _upgrade(client, "ok7@example.com").status_code == 200


def test_repeated_declines_stay_idempotent(client, make_subscriber):
    email = make_subscriber("fail8@example.com", days_out=30)
    billing_snapshot = copy.deepcopy(main.billing_data)

    for _ in range(5):
        assert _upgrade(client, email).status_code == 402

    assert main.billing_data == billing_snapshot


def test_the_guards_still_run_before_the_gateway_for_a_fail_email(client, make_subscriber):
    """A fail-prefixed Premium subscriber gets 409, not 402 - guards precede the charge."""
    email = make_subscriber("fail9@example.com", days_out=30)
    main.billing_data[email]["plan_name"] = "Premium"

    res = _upgrade(client, email)

    assert res.status_code == 409


def test_an_unknown_fail_caller_gets_401_not_402(client):
    """Authentication precedes the gateway, so no charge is ever attempted for a stranger."""
    res = _upgrade(client, "failunknown@example.com")
    assert res.status_code == 401


# ---------------------------------------------------------------------------
# Regression test for code-review finding F1 (v1 review, Blocker).
#
# Zone C once ended with `record["on_demand_usage"]["notice"] = ...`, a nested subscript that raises
# KeyError when the key is absent - after five writes had already landed. That left a record billed
# as Premium with Standard quotas and a Standard notice. The containers are now resolved in Zone B,
# so the failure happens before the first write.
# ---------------------------------------------------------------------------


def test_a_malformed_billing_record_does_not_produce_a_partial_upgrade(make_subscriber):
    """F1: an unexpected KeyError must leave the record completely unmodified."""
    from fastapi.testclient import TestClient

    email = make_subscriber("f1a@example.com", days_out=30)
    del main.billing_data[email]["on_demand_usage"]

    snapshot_billing = copy.deepcopy(main.billing_data[email])
    snapshot_user = copy.deepcopy(main.users[email])

    local_client = TestClient(main.app, raise_server_exceptions=False)
    res = local_client.post("/api/billing/upgrade", json={"email": email})

    # The request fails - that is acceptable for a malformed record. What is NOT acceptable is a
    # half-applied upgrade.
    assert res.status_code >= 400
    assert main.billing_data[email] == snapshot_billing
    assert main.users[email] == snapshot_user
    assert main.billing_data[email]["plan_name"] == "Standard"
    assert main.users[email]["plan"] == "Standard"


def test_a_billing_record_without_usages_does_not_produce_a_partial_upgrade(make_subscriber):
    """The same invariant for the other container Zone B resolves."""
    from fastapi.testclient import TestClient

    email = make_subscriber("f1b@example.com", days_out=30)
    del main.billing_data[email]["usages"]

    snapshot_billing = copy.deepcopy(main.billing_data[email])
    snapshot_user = copy.deepcopy(main.users[email])

    local_client = TestClient(main.app, raise_server_exceptions=False)
    res = local_client.post("/api/billing/upgrade", json={"email": email})

    assert res.status_code >= 400
    assert main.billing_data[email] == snapshot_billing
    assert main.users[email] == snapshot_user
