# Cycle-level cross-unit journeys: Epic 7344 Premium Upgrade Demo (Frontend Only)
#
# This cycle has ONE work unit (Story 1.1), so there are no story-to-story seams.
# The only genuine cross-boundary journey joins the EXISTING system (login, session,
# GET /api/billing in src/backend/main.py) to the new upgrade behaviour and back again
# through a reload. It is not a copy of any spec/behavior/story-1.1.feature scenario:
# it spans the auth flow, the unchanged backend contract and the full page lifecycle.

Feature: Premium upgrade demo, end to end across the existing login and billing flow

  Background:
    Given the backend is running with its seeded in-memory data
    And a registered user "tpg@example.com" with password "password" exists on the "Standard" plan at "$20/month"

  @REQ-F-01 @REQ-F-03 @REQ-F-10 @REQ-NF-01 @REQ-NF-02
  Scenario: A Standard subscriber logs in, upgrades to Premium, and a reload restores Standard
    When the user logs in as "tpg@example.com" with password "password"
    And the user opens the Billing page
    Then the current plan shows "Standard" at "$20/month"
    And the "Upgrade to Premium" button is visible
    When the user clicks "Upgrade to Premium"
    Then the current plan shows "Premium" at "$40/month"
    And the message "You're now on Premium!" is shown
    And no request was sent to the backend after the Billing page loaded
    When the user reloads the Billing page
    Then the current plan shows "Standard" at "$20/month"
    And the "Upgrade to Premium" button is visible
    And the user is still logged in
