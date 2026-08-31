"""The dummy payment gateway — FR-12, SEC-4, AC-16, AC-17."""

import inspect

import pytest

import main


@pytest.mark.parametrize(
    "email,expected",
    [
        ("tpg@example.com", "success"),
        ("notfail@example.com", "success"),
        ("myfail@example.com", "success"),
        ("fail@example.com", "card_declined"),
        ("failure@example.com", "card_declined"),
        ("fail", "card_declined"),
    ],
)
def test_outcome_is_decided_by_the_email_prefix(email, expected):
    assert main.charge_card(email, 19.33)["status"] == expected


def test_the_prefix_check_is_case_sensitive():
    """The Epic specifies a lowercase `fail` prefix, so Fail@ must succeed.

    Pinned as a test because "make it case-insensitive" is a plausible-looking change that would
    silently break persona P3's ability to demo the success path with a capitalised address.
    """
    assert main.charge_card("Fail@example.com", 1.0)["status"] == "success"
    assert main.charge_card("FAIL@example.com", 1.0)["status"] == "success"


def test_declined_result_carries_the_exact_contract_message():
    result = main.charge_card("fail@example.com", 19.33)
    assert result == {"status": "card_declined", "message": "Your card was declined."}


def test_success_result_carries_no_message_field():
    """The success shape is exactly {"status": "success"} - nothing extra leaks out."""
    assert main.charge_card("tpg@example.com", 19.33) == {"status": "success"}


def test_the_gateway_is_deterministic():
    """Persona P3 depends on the same email always producing the same outcome."""
    for _ in range(50):
        assert main.charge_card("fail@example.com", 19.33)["status"] == "card_declined"
        assert main.charge_card("tpg@example.com", 19.33)["status"] == "success"


@pytest.mark.parametrize("amount", [0.0, 0.67, 19.33, 20.0, -1.0, 1e9])
def test_the_amount_does_not_influence_the_outcome(amount):
    """Only the email decides. An amount-dependent gateway would be non-deterministic to demo."""
    assert main.charge_card("tpg@example.com", amount)["status"] == "success"
    assert main.charge_card("fail@example.com", amount)["status"] == "card_declined"


def _code_without_docstring(fn) -> str:
    """Return a function's source with its docstring removed.

    The docstring must be excluded: it legitimately describes the absence of logging, so scanning
    it would match the very word the test is asserting is absent from the code.
    """
    source = inspect.getsource(fn)
    doc = inspect.getdoc(fn)
    if doc:
        for line in doc.splitlines():
            source = source.replace(line, "")
    return source


def test_the_gateway_performs_no_io_and_no_logging():
    """SEC-4 / AC-17: nothing is emitted, so there is nothing to redact.

    Asserted against the function's own code rather than by monkeypatching, because the point is
    that the code contains no such call at all.
    """
    code = _code_without_docstring(main.charge_card)
    for forbidden in ("print(", "logging", "logger", "open(", "requests.", "httpx.", "urllib"):
        assert forbidden not in code, f"gateway must not contain {forbidden!r}"


def test_the_new_backend_code_contains_no_logging_at_all():
    """Constraint ARCH-06, across every unit this story added, not just the gateway."""
    for fn in (main.charge_card, main._resolve_upgrade_context, main._premium_usages,
               main.billing_upgrade_preview, main.billing_upgrade):
        code = _code_without_docstring(fn)
        for forbidden in ("print(", "logging.", "logger.", "sys.stdout", "sys.stderr"):
            assert forbidden not in code, f"{fn.__name__} must not contain {forbidden!r}"


def test_the_gateway_signature_accepts_no_card_data():
    """No card parameter exists, so no card value can be stored, logged, or leaked."""
    params = list(inspect.signature(main.charge_card).parameters)
    assert params == ["email", "amount"]
