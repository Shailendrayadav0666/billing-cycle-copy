# Story 1.5 — Switch the plan display to Premium on click
# Covers: REQ-F-03, REQ-F-04, REQ-F-05, REQ-F-06, REQ-F-08, REQ-NF-01, REQ-NF-04, REQ-NF-07, REQ-NF-09
# Epic: HELIX-7344 | AIRE Framework v1.0

Feature: Switch the plan display to Premium on click

  Background:
    Given a signed-in subscriber
    And the billing response has plan_name "Standard", price "$20/month" and renew date "Oct 30, 2026"
    And the subscriber is on the Billing page

  @AC-1
  Scenario: Clicking Upgrade switches the page to Premium instantly with no request
    When the subscriber clicks "Upgrade to Premium"
    Then the "Current plan" badge reads "Premium"
    And the section heading reads "What's included with Premium"
    And no additional network request has been made after the initial billing request
    And the page has not reloaded
    And no confirmation dialog is shown
    And nothing about the plan is written to localStorage, sessionStorage or cookies

  @AC-2
  Scenario: The price switches to the Premium price
    When the subscriber clicks "Upgrade to Premium"
    Then the price reads "$25/month"

  @AC-3
  Scenario: The usage cards switch to the Premium values
    When the subscriber clicks "Upgrade to Premium"
    Then the usage cards appear in the order "Video quality", "Watch at the same time", "Download on devices"
    And "Video quality" shows "4K Ultra HD + HDR"
    And the "Video quality" tooltip reads "The best video resolution available on the Premium plan."
    And "Watch at the same time" shows "Can watch on 4 devices at once"
    And the "Watch at the same time" tooltip reads "Number of supported devices that can stream on your account simultaneously."
    And "Download on devices" shows "Can download on 6 devices"
    And the "Download on devices" tooltip reads "Number of supported devices you can download titles to for offline viewing."

  @AC-4
  Scenario: The plan perks switch to the Premium perks
    When the subscriber clicks "Upgrade to Premium"
    Then the "Plan perks" card lists "Ad-free streaming", "Spatial audio (select titles)" and "Dolby Atmos (select titles)"
    And each perk shows "100% used"
    And the perks help text reads "Perks included in your Premium plan."

  @AC-5
  Scenario: The renewal date does not change
    When the subscriber clicks "Upgrade to Premium"
    Then "Renew at" still reads "Oct 30, 2026"
