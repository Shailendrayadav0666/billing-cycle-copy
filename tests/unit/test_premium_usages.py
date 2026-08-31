"""The quota-ceiling transform — FR-13, NFR-C7, NFR-M4, AC-21, AC-22.

This is the transform the Epic's own design would have got wrong: its PREMIUM_QUOTAS declared
complete usage objects carrying used: 0, which would have reset consumption. These tests pin the
corrected behaviour.
"""

import copy

import main


def _standard_usages():
    return [
        {"id": "chat-credits", "label": "Chat credits", "used": 100, "total": 2000, "help": "h1"},
        {"id": "chatbots", "label": "Chatbots", "used": 1, "total": 3, "help": "h2"},
        {
            "id": "documents-pages",
            "label": "Documents pages",
            "used": 15,
            "total": 1000,
            "help": "You can add 985 more pages of your documents.",
        },
    ]


def test_totals_are_raised_to_the_premium_ceilings():
    result = {u["id"]: u for u in main._premium_usages(_standard_usages())}
    assert result["chat-credits"]["total"] == 10000
    assert result["chatbots"]["total"] == 10
    assert result["documents-pages"]["total"] == 5000


def test_consumption_is_preserved():
    """AC-21: an upgrade raises the ceiling; it never resets what has been consumed."""
    result = {u["id"]: u for u in main._premium_usages(_standard_usages())}
    assert result["chat-credits"]["used"] == 100
    assert result["chatbots"]["used"] == 1
    assert result["documents-pages"]["used"] == 15


def test_ids_and_labels_are_preserved():
    before = _standard_usages()
    after = main._premium_usages(before)
    assert [u["id"] for u in after] == [u["id"] for u in before]
    assert [u["label"] for u in after] == [u["label"] for u in before]


def test_order_is_preserved():
    before = _standard_usages()
    after = main._premium_usages(before)
    assert [u["id"] for u in after] == ["chat-credits", "chatbots", "documents-pages"]


def test_the_input_list_is_not_mutated():
    """NFR-M4: the transform is pure, which is what makes build-then-assign safe."""
    before = _standard_usages()
    snapshot = copy.deepcopy(before)
    main._premium_usages(before)
    assert before == snapshot


def test_it_returns_a_new_list_and_new_entry_objects():
    before = _standard_usages()
    after = main._premium_usages(before)
    assert after is not before
    for original, upgraded in zip(before, after):
        assert original is not upgraded


def test_documents_pages_help_states_remaining_capacity():
    """AC-22 / BR-6: follows the convention the existing seed and registration data already use."""
    result = {u["id"]: u for u in main._premium_usages(_standard_usages())}
    assert result["documents-pages"]["help"] == "You can add 4985 more pages of your documents."


def test_other_help_texts_are_left_alone():
    result = {u["id"]: u for u in main._premium_usages(_standard_usages())}
    assert result["chat-credits"]["help"] == "h1"
    assert result["chatbots"]["help"] == "h2"


def test_an_unknown_quota_id_passes_through_untouched():
    """Forward-compatible: a future metric must not be silently dropped by an upgrade."""
    usages = _standard_usages() + [
        {"id": "future-metric", "label": "Future", "used": 7, "total": 42, "help": "h4"}
    ]
    result = main._premium_usages(usages)
    future = [u for u in result if u["id"] == "future-metric"][0]
    assert future == {"id": "future-metric", "label": "Future", "used": 7, "total": 42, "help": "h4"}
    assert len(result) == 4


def test_an_empty_list_yields_an_empty_list():
    assert main._premium_usages([]) == []


def test_premium_totals_match_the_epic_specification():
    assert main.PREMIUM_QUOTA_TOTALS == {
        "chat-credits": 10000,
        "chatbots": 10,
        "documents-pages": 5000,
    }


def test_the_premium_notice_is_the_exact_contract_string():
    assert main.PREMIUM_ON_DEMAND_NOTICE == "On-demand credit is available on your Premium plan."
