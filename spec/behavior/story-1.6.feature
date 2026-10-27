# Story 1.6 — Post-upgrade confirmation
# Covers: REQ-F-09, REQ-F-10, REQ-F-11, REQ-NF-02, REQ-NF-03, REQ-NF-07 | Epic: HELIX-7344 | AIRE Framework v1.0

Feature: Post-upgrade confirmation

  Background:
    Given a signed-in subscriber
    And the billing response has plan_name "Standard", price "$20/month" and renew date "Oct 30, 2026"
    And the subscriber is on the Billing page

  @AC-1
  Scenario: A success banner confirms the upgrade
    When the subscriber clicks "Upgrade to Premium"
    Then a success banner is shown at the top of the Billing page
    And the banner reads exactly "You're now on Premium! Enjoy 4K Ultra HD, more screens and more downloads."

  @AC-1
  Scenario: No success banner before the upgrade
    Then no success banner is shown

  @AC-2
  Scenario: The success banner is announced to screen readers
    When the subscriber clicks "Upgrade to Premium"
    Then the banner has role "status"
    And the banner is a polite live region

  @AC-3
  Scenario: The success banner stays on screen
    When the subscriber clicks "Upgrade to Premium"
    And 10 seconds pass
    Then the success banner is still shown
    And the banner has no close button

  @AC-4
  Scenario: The Upgrade button disappears after the upgrade
    When the subscriber clicks "Upgrade to Premium"
    Then no button named "Upgrade to Premium" is shown

  @AC-5
  Scenario: A reload returns the page to Standard
    Given the subscriber has clicked "Upgrade to Premium"
    When the Billing page is reloaded
    Then the billing request is sent again
    And the "Current plan" badge reads "Standard"
    And a button named "Upgrade to Premium" is shown
    And no success banner is shown
