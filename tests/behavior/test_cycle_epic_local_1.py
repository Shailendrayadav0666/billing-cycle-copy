"""B3 tier — epic scope. Single-unit cycle (Story 1 is the whole epic, per the
user's explicit single-story override — see spec/plans/stories.md granularity
note). Runs immediately per common/behavior-spec.md Section 6.1 ("Single-unit
cycles: there are no other units, so the condition is satisfied immediately").
"""

from pytest_bdd import scenarios

from tests.behavior.steps.billing_steps import *  # noqa: F401,F403

scenarios("../../spec/behavior.feature")
