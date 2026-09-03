"""B1 tier — this work unit's own behaviour spec."""

from pytest_bdd import scenarios

from tests.behavior.steps.billing_steps import *  # noqa: F401,F403

scenarios("../../spec/behavior/story-1.feature")
