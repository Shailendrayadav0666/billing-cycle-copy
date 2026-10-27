# Story 1.3 — Fail-safe billing fetch
# Covers: REQ-NF-08 | Epic: HELIX-7344 | AIRE Framework v1.0

Feature: Fail-safe billing fetch

  Background:
    Given a signed-in subscriber

  @AC-1
  Scenario: A rejected billing request is caught and the page stays on loading
    Given the billing request fails with a network error
    When the subscriber opens the Billing page
    Then no unhandled promise rejection is raised
    And the page shows "Loading billing..."

  @AC-2
  Scenario: A 401 response is not used as billing data
    Given the billing request returns status 401 with body detail "Not authenticated"
    When the subscriber opens the Billing page
    Then the page does not crash
    And the page shows "Loading billing..."
    And no "Current plan" badge, price or usage card is shown

  @AC-2
  Scenario: A 500 response is not used as billing data
    Given the billing request returns status 500
    When the subscriber opens the Billing page
    Then the page does not crash
    And the page shows "Loading billing..."

  @AC-3
  Scenario: No internal error detail is shown to the subscriber
    Given the billing request returns status 401 with body detail "Not authenticated"
    When the subscriber opens the Billing page
    Then the page does not show "401"
    And the page does not show "Not authenticated"
    And the page does not show any stack trace or error message

  @AC-1
  Scenario: A successful billing request still renders the page
    Given the billing request returns status 200 with plan_name "Standard" and price "$20/month"
    When the subscriber opens the Billing page
    Then the price reads "$20/month"
