# Cycle-level cross-unit journeys for HELIX-7344 (Premium Upgrade Demo, Frontend Only).
# Each scenario spans several stories and only becomes testable once those stories exist.
# Per-story behaviour lives in spec/behavior/story-<N.M>.feature and is NOT repeated here.
# AIRE Framework v1.0

Feature: Premium upgrade demo - end to end on the Billing page

  Background:
    Given a signed-in subscriber whose billing response has plan_name "Standard", price "$20/month" and renew date "Oct 30, 2026"

  @REQ-F-01 @REQ-F-03 @REQ-F-07 @REQ-F-09 @REQ-F-10
  Scenario: A Standard subscriber upgrades and the whole page confirms Premium
    When the subscriber opens the Billing page
    Then the "Current plan" badge reads "Standard"                                   # story 1.2
    And an "Upgrade to Premium" button is shown in the page header                  # story 1.4
    When the subscriber clicks "Upgrade to Premium"                                 # story 1.5
    Then the "Current plan" badge reads "Premium"                                    # story 1.2 rule, driven by 1.5
    And the price reads "$25/month"                                                  # story 1.5
    And the success banner reads "You're now on Premium! Enjoy 4K Ultra HD, more screens and more downloads."  # story 1.6
    And no "Upgrade to Premium" button is shown                                     # story 1.6

  @REQ-F-11 @REQ-F-02
  Scenario: The demo can be shown again after a reload
    Given the subscriber has upgraded to Premium on the Billing page
    When the subscriber reloads the Billing page
    Then the "Current plan" badge reads "Standard"                                   # story 1.2
    And an "Upgrade to Premium" button is shown in the page header                  # story 1.4
    And no success banner is shown                                                  # story 1.6
    When the subscriber clicks "Upgrade to Premium" again                           # story 1.5
    Then the "Current plan" badge reads "Premium"                                    # story 1.2 rule, driven by 1.5
    And the success banner is shown                                                 # story 1.6

  @REQ-NF-08 @REQ-F-01
  Scenario: A failed billing load never offers the upgrade
    Given the billing request fails with status 401
    When the subscriber opens the Billing page
    Then the page shows "Loading billing..."                                         # story 1.3
    And no "Upgrade to Premium" button is shown                                     # story 1.4
    And no success banner is shown                                                  # story 1.6
