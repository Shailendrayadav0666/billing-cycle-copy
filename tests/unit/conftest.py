"""Shared fixtures for Story 1.1.

The backend's data layer is three module-level dicts, so any test that mutates them would leak
into every later test. Every fixture here deep-copies the stores before a test and restores them
afterwards, which is what makes the declined-path "nothing changed" assertions trustworthy.
"""

import copy
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient

import main

SEED_EMAIL = "tpg@example.com"
FAIL_EMAIL = "fail@example.com"


@pytest.fixture(autouse=True)
def isolate_stores():
    """Restore the module-level stores after every test."""
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
def client():
    return TestClient(main.app)


def _renew_at(days_from_today: int) -> str:
    return (datetime.today() + timedelta(days=days_from_today)).strftime("%b %d, %Y")


@pytest.fixture
def make_subscriber():
    """Create a Standard subscriber with a renewal date a given number of days out.

    Returns the email. Used instead of hardcoding a date, because renew_at is dynamic in this
    codebase and any fixed date would make the tests fail once the clock passes it.
    """

    def _make(email: str, days_out: int = 30, used=(100, 1, 15)):
        main.users[email] = {
            "id": len(main.users) + 1,
            "name": "Test",
            "email": email,
            "password": "password",
            "plan": "Standard",
            "price": "$20/month",
            "renew_at": _renew_at(days_out),
        }
        chat_used, bot_used, page_used = used
        main.billing_data[email] = {
            "plan_name": "Standard",
            "price": "$20/month",
            "renew_at": _renew_at(days_out),
            "usages": [
                {
                    "id": "chat-credits",
                    "label": "Chat credits",
                    "used": chat_used,
                    "total": 2000,
                    "help": "Messages used this billing cycle.",
                },
                {
                    "id": "chatbots",
                    "label": "Chatbots",
                    "used": bot_used,
                    "total": 3,
                    "help": "Active chatbot agents out of the included limit.",
                },
                {
                    "id": "documents-pages",
                    "label": "Documents pages",
                    "used": page_used,
                    "total": 1000,
                    "help": f"You can add {1000 - page_used} more pages of your documents.",
                },
            ],
            "included_usage": {
                "title": "Your included usage",
                "items": [
                    {"id": "daily", "label": "Daily quota", "used_percent": 5, "resets_in": "23 hours"},
                ],
                "help": "Usage included in your plan.",
            },
            "on_demand_usage": {
                "title": "On-demand usage",
                "remaining_balance": "$18.00",
                "your_usage": "$0.00",
                "help": "Additional usage charges beyond your included quota.",
                "notice": (
                    "On-demand credit is not available in standard plan for usage beyond "
                    "your included quota."
                ),
            },
        }
        return email

    return _make


def expected_charge(days_remaining: int) -> float:
    """The proration formula, expressed independently of the implementation.

    Deliberately recomputed here rather than imported, so a change to the production formula does
    not silently change what the tests consider correct.
    """
    return round((40.0 - 20.0) / 30 * days_remaining, 2)
