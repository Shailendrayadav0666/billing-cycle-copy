Feature: Mid-Cycle Subscription Upgrade (Standard -> Premium)

  Background:
    Given a user "priya@example.com" exists with an active "Standard" subscription at $20/month
    And a user "fail@example.com" exists with an active "Standard" subscription at $20/month
    And a user "premium@example.com" exists with an active "Premium" subscription at $40/month

  @AC-1
  Scenario: Standard subscriber sees the Upgrade to Premium CTA and dynamic plan badge
    When "priya@example.com" views the Billing page
    Then the plan badge shows "Standard"
    And an "Upgrade to Premium" button is shown

  @AC-1
  Scenario: Premium subscriber sees no Upgrade to Premium CTA
    When "premium@example.com" views the Billing page
    Then the plan badge shows "Premium"
    And no "Upgrade to Premium" button is shown

  @AC-2
  @AC-3
  Scenario: Proration preview returns the exact server-computed charge
    When "priya@example.com" requests the upgrade preview
    Then the response is 200
    And the response contains current_plan "Standard" and new_plan "Premium"
    And the prorated charge equals ((40.00 - 20.00) / 30) times the days remaining, rounded to 2 decimals

  @AC-5
  Scenario: Successful upgrade flips the plan and updates quotas
    Given "priya@example.com" has confirmed the upgrade preview
    When "priya@example.com" confirms the upgrade
    Then the response is 200 with status "success" and plan "Premium"
    And "priya@example.com" plan_name becomes "Premium"
    And "priya@example.com" usages become chat-credits 10000, chatbots 10, documents-pages 5000
    And "priya@example.com" renew_at is unchanged

  @AC-6
  Scenario: Billing page reflects the successful upgrade
    Given "priya@example.com" has just upgraded successfully
    When "priya@example.com" views the Billing page
    Then the plan badge shows "Premium"
    And no "Upgrade to Premium" button is shown

  @AC-7
  Scenario: Declined payment leaves Standard plan untouched
    When "fail@example.com" confirms the upgrade
    Then the response is 402 with detail "card_declined"
    And "fail@example.com" plan_name remains "Standard"
    And "fail@example.com" usages are unchanged

  @AC-8
  Scenario: Already-Premium guard on the preview endpoint
    When "premium@example.com" requests the upgrade preview
    Then the response is 409 with detail "already_premium"

  @AC-8
  Scenario: Already-Premium guard on the upgrade endpoint
    When "premium@example.com" confirms the upgrade
    Then the response is 409 with detail "already_premium"
    And "premium@example.com" is not charged

  @AC-9
  Scenario: Auth, tasks, login and registration endpoints are unaffected
    When the existing auth, tasks, login and registration endpoints are called as before
    Then they behave exactly as they did before this story
