# Story 1.2 — Plan text follows the current plan
# Covers: REQ-F-07, REQ-F-12, REQ-NF-03 | Epic: HELIX-7344 | AIRE Framework v1.0

Feature: Plan text follows the current plan

  Background:
    Given a signed-in subscriber
    And the billing response has price "$20/month", renew date "Oct 30, 2026", three usage cards and two plan perks

  @AC-1
  Scenario: Standard plan text comes from the billing response
    Given the billing response has plan_name "Standard"
    When the subscriber opens the Billing page
    Then the "Current plan" badge reads "Standard"
    And the section heading reads "What's included with Standard"

  @AC-2
  Scenario: Premium plan text and badge style
    Given the current plan is "Premium"
    When the Billing page renders
    Then the "Current plan" badge reads "Premium"
    And the badge uses the Premium badge style, not the Standard badge style
    And the section heading reads "What's included with Premium"

  @AC-3
  Scenario: The rest of the page renders exactly as before
    Given the billing response has plan_name "Standard"
    When the subscriber opens the Billing page
    Then the page subtitle reads "Manage your plan and payments"
    And the plan card label reads "Monthly plan"
    And the plan card shows the "Active" badge
    And the section sub-copy reads "Unlimited movies, TV shows and more. Watch anywhere. Cancel anytime."

  @AC-4
  Scenario: The loading state is unchanged while the response is pending
    Given the billing response has not arrived yet
    When the Billing page renders
    Then the page shows "Loading billing..."
    And no "Current plan" badge is shown
