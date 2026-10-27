# Story 1.4 — Upgrade button on the Standard plan
# Covers: REQ-F-01, REQ-F-02, REQ-NF-02, REQ-NF-03 | Epic: HELIX-7344 | AIRE Framework v1.0

Feature: Upgrade button on the Standard plan

  Background:
    Given a signed-in subscriber
    And the billing response has price "$20/month" and renew date "Oct 30, 2026"

  @AC-1
  Scenario: A Standard subscriber sees the Upgrade button in the page header
    Given the billing response has plan_name "Standard"
    When the subscriber opens the Billing page
    Then a button named "Upgrade to Premium" is shown
    And the button sits in the page header on the same row as the "Plan & Billing" title, aligned to the right

  @AC-2
  Scenario: A Premium subscriber does not see the Upgrade button
    Given the billing response has plan_name "Premium"
    When the subscriber opens the Billing page
    Then no button named "Upgrade to Premium" is shown

  @AC-2
  Scenario: A plan name that is not exactly "Standard" hides the Upgrade button
    Given the billing response has plan_name "standard"
    When the subscriber opens the Billing page
    Then no button named "Upgrade to Premium" is shown

  @AC-2
  Scenario: No Upgrade button while billing is still loading
    Given the billing response has not arrived yet
    When the Billing page renders
    Then no button named "Upgrade to Premium" is shown

  @AC-3
  Scenario: The Upgrade button works from the keyboard
    Given the billing response has plan_name "Standard"
    When the subscriber moves focus to "Upgrade to Premium" with the Tab key
    Then the focused element is a native button with the visible text "Upgrade to Premium"
    And a visible focus outline is shown on it
    When the subscriber presses Enter
    Then the upgrade action is invoked once
    When the subscriber presses Space on the button
    Then the upgrade action is invoked again
