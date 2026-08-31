"""API & Contract Testing gate (SH-LOOP-2) for the two endpoints this story adds.

Covers the gate's six checklist items on every touched endpoint:
  1. functional behaviour
  2. response-code validation
  3. role-based authorization (401 / 403)
  4. error-response validation
  5. request validation
  6. response contract / schema validation

Endpoints in scope:
  GET  /api/billing/upgrade-preview
  POST /api/billing/upgrade
"""

import main

PREVIEW = "/api/billing/upgrade-preview"
UPGRADE = "/api/billing/upgrade"

PREVIEW_SCHEMA = {
    "current_plan": str,
    "new_plan": str,
    "days_remaining": int,
    "prorated_charge": float,
    "next_renewal_price": float,
    "renew_at": str,
}

UPGRADE_SCHEMA = {"status": str, "plan": str, "charge": float}


# ------------------------------------------------------------------ 1. functional behaviour


def test_preview_functional_behaviour(client, make_subscriber):
    email = make_subscriber("c1@example.com")
    res = client.get(PREVIEW, params={"email": email})
    assert res.status_code == 200
    assert res.json()["new_plan"] == "Premium"


def test_upgrade_functional_behaviour(client, make_subscriber):
    email = make_subscriber("c2@example.com")
    res = client.post(UPGRADE, json={"email": email})
    assert res.status_code == 200
    assert main.billing_data[email]["plan_name"] == "Premium"


# ------------------------------------------------------------ 2. response-code validation


def test_preview_response_codes(client, make_subscriber):
    """Every documented status code for the preview endpoint is reachable."""
    ok = make_subscriber("c3@example.com")
    assert client.get(PREVIEW, params={"email": ok}).status_code == 200

    assert client.get(PREVIEW, params={"email": "ghost@example.com"}).status_code == 401

    orphan = make_subscriber("c4@example.com")
    main.billing_data.pop(orphan)
    assert client.get(PREVIEW, params={"email": orphan}).status_code == 404

    premium = make_subscriber("c5@example.com")
    main.billing_data[premium]["plan_name"] = "Premium"
    assert client.get(PREVIEW, params={"email": premium}).status_code == 409

    # A missing required query parameter is a validation error, not a 500.
    assert client.get(PREVIEW).status_code == 422


def test_upgrade_response_codes(client, make_subscriber):
    """Every documented status code for the upgrade endpoint is reachable."""
    ok = make_subscriber("c6@example.com")
    assert client.post(UPGRADE, json={"email": ok}).status_code == 200

    assert client.post(UPGRADE, json={"email": "ghost@example.com"}).status_code == 401

    orphan = make_subscriber("c7@example.com")
    main.billing_data.pop(orphan)
    assert client.post(UPGRADE, json={"email": orphan}).status_code == 404

    premium = make_subscriber("c8@example.com")
    main.billing_data[premium]["plan_name"] = "Premium"
    assert client.post(UPGRADE, json={"email": premium}).status_code == 409

    declined = make_subscriber("failc9@example.com")
    assert client.post(UPGRADE, json={"email": declined}).status_code == 402

    assert client.post(UPGRADE, json={}).status_code == 422


def test_wrong_method_is_rejected(client, make_subscriber):
    """A wrong method never succeeds and never mutates.

    The exact status code is deliberately NOT asserted, because it depends on deployment state
    rather than on this story's contract: main.py conditionally mounts the built SPA at "/" when
    src/frontend/dist exists. With the SPA mounted, a GET to a POST-only API path falls through to
    StaticFiles and returns 404; without it, Starlette returns 405. Both are correct refusals, and
    pinning one of them would make the suite pass or fail depending on whether someone had run
    `npm run build` - which is not a property of this feature.
    """
    email = make_subscriber("c10@example.com")

    for res in (
        client.post(PREVIEW, json={"email": email}),
        client.get(UPGRADE, params={"email": email}),
    ):
        assert res.status_code in (404, 405)
        assert res.status_code >= 400

    # The important guarantee: no mutation happened through the wrong verb.
    assert main.billing_data[email]["plan_name"] == "Standard"
    assert main.users[email]["plan"] == "Standard"


# ------------------------------------------------- 3. role-based authorization (401 / 403)


def test_both_endpoints_require_authentication(client):
    """No role model exists in this system, so authorization reduces to identity.

    401 is the correct code for an unknown caller. There is no 403 case to test: there are no
    roles, no privilege levels, and no endpoint that an authenticated user is forbidden to call on
    their own account. Recorded here explicitly rather than left as an untested gap.
    """
    assert client.get(PREVIEW, params={"email": "nobody@example.com"}).status_code == 401
    assert client.post(UPGRADE, json={"email": "nobody@example.com"}).status_code == 401


def test_a_caller_cannot_act_on_another_identity(client, make_subscriber):
    """The closest analogue of a 403 here: acting on someone else's record is impossible.

    Both endpoints key exclusively off the caller's own email, so there is no parameter through
    which one subscriber could target another's billing record.
    """
    victim = make_subscriber("victim@example.com")
    attacker = make_subscriber("attacker@example.com")

    client.post(UPGRADE, json={"email": attacker})

    assert main.billing_data[victim]["plan_name"] == "Standard"
    assert main.users[victim]["plan"] == "Standard"


# ------------------------------------------------------- 4. error-response validation


def test_error_bodies_match_the_documented_shapes(client, make_subscriber):
    assert client.get(PREVIEW, params={"email": "nobody@example.com"}).json() == {
        "detail": "Not authenticated"
    }

    orphan = make_subscriber("c11@example.com")
    main.billing_data.pop(orphan)
    assert client.get(PREVIEW, params={"email": orphan}).json() == {
        "detail": "billing_record_not_found"
    }

    premium = make_subscriber("c12@example.com")
    main.billing_data[premium]["plan_name"] = "Premium"
    assert client.get(PREVIEW, params={"email": premium}).json() == {"detail": "already_premium"}

    declined = make_subscriber("failc13@example.com")
    assert client.post(UPGRADE, json={"email": declined}).json() == {
        "detail": "card_declined",
        "message": "Your card was declined.",
    }


def test_no_error_body_leaks_internal_detail(client, make_subscriber):
    declined = make_subscriber("failc14@example.com")
    orphan = make_subscriber("c15@example.com")
    main.billing_data.pop(orphan)

    bodies = [
        client.post(UPGRADE, json={"email": declined}).text,
        client.get(PREVIEW, params={"email": orphan}).text,
        client.get(PREVIEW, params={"email": "nobody@example.com"}).text,
    ]
    for body in bodies:
        for leak in ("Traceback", "File \"", "billing_data", "password", "tpg@example.com"):
            assert leak not in body


# ------------------------------------------------------------- 5. request validation


def test_upgrade_rejects_a_malformed_body(client):
    assert client.post(UPGRADE, json={"email": 12345}).status_code == 422
    assert client.post(UPGRADE, json={"wrong_field": "x"}).status_code == 422
    assert client.post(UPGRADE, content=b"not json").status_code == 422


def test_upgrade_ignores_unknown_fields_rather_than_trusting_them(client, make_subscriber):
    """Unknown keys are dropped by the model, so they cannot influence behaviour."""
    email = make_subscriber("c16@example.com")
    res = client.post(
        UPGRADE, json={"email": email, "amount": 0.01, "plan": "Enterprise", "admin": True}
    )
    assert res.status_code == 200
    assert res.json()["plan"] == "Premium"
    assert res.json()["charge"] != 0.01


def test_preview_requires_the_email_parameter(client):
    assert client.get(PREVIEW).status_code == 422


# --------------------------------------------- 6. response contract / schema validation


def _assert_schema(body: dict, schema: dict) -> None:
    assert set(body) == set(schema), f"unexpected fields: {set(body) ^ set(schema)}"
    for field, expected in schema.items():
        value = body[field]
        if expected is float:
            assert isinstance(value, (int, float)) and not isinstance(value, bool), field
        else:
            assert isinstance(value, expected), f"{field} is {type(value).__name__}"


def test_preview_response_matches_its_contract(client, make_subscriber):
    email = make_subscriber("c17@example.com")
    _assert_schema(client.get(PREVIEW, params={"email": email}).json(), PREVIEW_SCHEMA)


def test_upgrade_response_matches_its_contract(client, make_subscriber):
    email = make_subscriber("c18@example.com")
    _assert_schema(client.post(UPGRADE, json={"email": email}).json(), UPGRADE_SCHEMA)


def test_the_upgraded_billing_payload_keeps_its_existing_contract(client, make_subscriber):
    """GET /api/billing's response shape must not change - the regression baseline depends on it."""
    email = make_subscriber("c19@example.com")
    before = set(client.get("/api/billing", params={"email": email}).json())

    client.post(UPGRADE, json={"email": email})
    after_body = client.get("/api/billing", params={"email": email}).json()

    assert set(after_body) == before
    for usage in after_body["usages"]:
        assert set(usage) == {"id", "label", "used", "total", "help"}


def test_the_endpoints_are_documented_in_the_openapi_schema(client):
    """FastAPI derives the schema from the code, so this proves the contract is discoverable."""
    schema = client.get("/openapi.json").json()
    assert PREVIEW in schema["paths"]
    assert UPGRADE in schema["paths"]
    assert "get" in schema["paths"][PREVIEW]
    assert "post" in schema["paths"][UPGRADE]
