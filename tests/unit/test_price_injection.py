"""The client cannot choose its own price — SEC-3, SEC-6, AC-18, constraint ARCH-02."""

import inspect

import main
from conftest import expected_charge


def test_an_amount_in_the_request_body_is_ignored(client, make_subscriber):
    """AC-18: the server-computed value is charged, not the caller's."""
    email = make_subscriber("inj1@example.com", days_out=30)
    preview = client.get("/api/billing/upgrade-preview", params={"email": email}).json()

    res = client.post(
        "/api/billing/upgrade",
        json={"email": email, "amount": 0.01, "prorated_charge": 0.01, "charge": 0.01},
    )

    assert res.status_code == 200
    assert res.json()["charge"] == preview["prorated_charge"]
    assert res.json()["charge"] != 0.01


def test_a_negative_amount_cannot_be_injected(client, make_subscriber):
    email = make_subscriber("inj2@example.com", days_out=30)
    res = client.post("/api/billing/upgrade", json={"email": email, "amount": -999.0})

    assert res.status_code == 200
    assert res.json()["charge"] > 0


def test_a_plan_field_cannot_be_injected(client, make_subscriber):
    """The target plan is not caller-supplied either."""
    email = make_subscriber("inj3@example.com", days_out=30)
    res = client.post("/api/billing/upgrade", json={"email": email, "plan": "Enterprise"})

    assert res.status_code == 200
    assert res.json()["plan"] == "Premium"
    assert main.billing_data[email]["plan_name"] == "Premium"


def test_the_request_model_declares_exactly_one_field():
    """SEC-3: realised as an absence of capability, not as a validation rule.

    There is no amount field for a caller to populate, so there is no variable in the handler that
    could carry an injected price.
    """
    assert list(main.UpgradeRequest.model_fields) == ["email"]


def test_no_request_model_exposes_a_monetary_field():
    """Constraint ARCH-02, asserted across every request model in the module."""
    forbidden = {"amount", "price", "charge", "total", "cost"}
    for name, obj in vars(main).items():
        if inspect.isclass(obj) and issubclass(obj, main.BaseModel) and obj is not main.BaseModel:
            fields = set(obj.model_fields)
            assert not (fields & forbidden), f"{name} exposes a monetary field: {fields & forbidden}"


def test_a_missing_email_is_rejected_by_the_model(client):
    res = client.post("/api/billing/upgrade", json={})
    assert res.status_code == 422


def test_the_charge_is_recomputed_rather_than_carried_from_the_preview(client, make_subscriber):
    """The POST does not trust, or even accept, the figure the preview returned."""
    email = make_subscriber("inj4@example.com", days_out=30)
    preview = client.get("/api/billing/upgrade-preview", params={"email": email}).json()

    res = client.post("/api/billing/upgrade", json={"email": email})

    assert res.json()["charge"] == expected_charge(preview["days_remaining"])


def test_the_upgrade_handler_contains_no_pricing_arithmetic_from_request_data():
    """The handler reads the amount only from the shared resolver, never from the payload."""
    source = inspect.getsource(main.billing_upgrade)
    assert "payload.amount" not in source
    assert "payload.price" not in source
    assert "payload.charge" not in source
