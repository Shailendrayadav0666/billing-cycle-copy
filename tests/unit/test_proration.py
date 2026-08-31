"""Proration correctness — NFR-C1..NFR-C4, AC-6, AC-7.

The input domain is an integer 1..30, which is small enough to verify exhaustively rather than
sample. No test here asserts a literal dollar amount: renew_at is computed at runtime, so any
hardcoded figure would encode today's date into the suite (requirement NFR-C4).
"""

from datetime import datetime, timedelta

import pytest

import main
from conftest import expected_charge


DOMAIN = range(1, 31)


@pytest.mark.parametrize("days_remaining", DOMAIN)
def test_formula_is_exact_across_the_whole_domain(days_remaining, make_subscriber):
    """NFR-C1: the formula is correct for every value days_remaining can take."""
    # +1 because parsing renew_at yields midnight while datetime.today() carries a time, so the
    # subtraction truncates by one day. This is the documented behaviour of finding F-2.
    email = make_subscriber(f"d{days_remaining}@example.com", days_out=days_remaining + 1)
    _record, resolved_days, charge = main._resolve_upgrade_context(email)

    assert resolved_days == days_remaining
    assert charge == expected_charge(days_remaining)


@pytest.mark.parametrize("days_remaining", DOMAIN)
def test_charge_stays_within_the_plan_difference_bounds(days_remaining, make_subscriber):
    """NFR-C3 / AC-7: one day's delta is the floor, a whole cycle's delta is the ceiling."""
    email = make_subscriber(f"b{days_remaining}@example.com", days_out=days_remaining + 1)
    _record, _days, charge = main._resolve_upgrade_context(email)

    assert charge > 0
    assert charge <= 20.00


@pytest.mark.parametrize("days_out", [0, 1, -5, -60])
def test_days_remaining_is_floored_at_one(days_out, make_subscriber):
    """NFR-C2 / AC-6: a cycle ending today, or already past, still costs one day - never zero."""
    email = make_subscriber(f"floor{abs(days_out)}@example.com", days_out=days_out)
    _record, resolved_days, charge = main._resolve_upgrade_context(email)

    assert resolved_days >= 1
    assert charge == expected_charge(1)


def test_rounding_produces_at_most_two_decimal_places(make_subscriber):
    """The charge is a money value, so it must never carry float noise into the response."""
    for days_out in DOMAIN:
        email = make_subscriber(f"r{days_out}@example.com", days_out=days_out + 1)
        _record, _days, charge = main._resolve_upgrade_context(email)
        assert round(charge, 2) == charge


def test_the_epics_illustrative_example_holds(make_subscriber):
    """The Epic quotes "15 days remaining -> $10.00" as an illustration of the formula.

    Asserting it here documents that the formula reproduces the Epic's worked example, without
    asserting that any real request will produce $10.00 - it will not, because renew_at is
    always 30 days out, giving 29 days remaining.
    """
    email = make_subscriber("fifteen@example.com", days_out=16)
    _record, resolved_days, charge = main._resolve_upgrade_context(email)

    assert resolved_days == 15
    assert charge == 10.00


def test_a_default_seeded_subscriber_yields_29_days_not_15(make_subscriber):
    """Finding F-2, pinned as a test so it cannot silently regress into the Epic's assumption."""
    email = make_subscriber("default@example.com", days_out=30)
    _record, resolved_days, charge = main._resolve_upgrade_context(email)

    assert resolved_days == 29
    assert charge == expected_charge(29)


def test_renew_at_parse_format_matches_how_it_is_written():
    """The stored format and the parse format must agree, or every quote raises."""
    written = (datetime.today() + timedelta(days=30)).strftime("%b %d, %Y")
    assert datetime.strptime(written, "%b %d, %Y")


def test_plan_prices_and_cycle_length_are_the_single_source():
    """No handler should carry a magic number; the constants are the source of truth."""
    assert main.PLANS["Standard"]["price"] == 20.0
    assert main.PLANS["Premium"]["price"] == 40.0
    assert main.PLANS["Premium"]["label"] == "$40/month"
    assert main.DAYS_IN_CYCLE == 30
