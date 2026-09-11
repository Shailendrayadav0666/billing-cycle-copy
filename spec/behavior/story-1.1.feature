Feature: Mid-Cycle Subscription Upgrade (Standard -> Premium)

  Background:
    Given a Standard subscriber "tpg@example.com" with 15 days remaining in the billing cycle

  @AC1
  Scenario: Standard subscriber sees the Upgrade CTA
    When the subscriber views the Billing page
    Then an "Upgrade to Premium" action is available

  @AC2
  Scenario: Plan badge reflects the real plan
    When the subscriber views the Billing page
    Then the plan badge shows "Standard"
    And the plan price shows "$20/month"

  @AC3
  Scenario: Confirmation preview shows the exact prorated charge
    When the subscriber requests the upgrade preview
    Then the preview shows current plan "Standard" and new plan "Premium"
    And the preview shows the prorated charge computed from the proration formula
    And the preview shows the next renewal price of "40.0"

  @AC4
  Scenario: Proration preview endpoint returns the documented contract
    When the subscriber requests "GET /api/billing/upgrade-preview"
    Then the response contains current_plan, new_plan, days_remaining, prorated_charge, next_renewal_price, renew_at

  @AC5
  Scenario: Successful upgrade charges the prorated amount and flips the plan
    Given the subscriber's email does not start with "fail"
    When the subscriber confirms the upgrade
    Then the payment gateway is charged the prorated amount
    And the response reports status "success" and plan "Premium"

  @AC6
  Scenario: Upgrade applies Premium quotas and preserves the renewal date
    Given the subscriber's email does not start with "fail"
    When the subscriber confirms the upgrade
    Then the plan becomes "Premium" with price "$40/month"
    And the chat credits quota becomes 10000
    And the chatbots quota becomes 10
    And the documents pages quota becomes 5000
    And the renew_at date is unchanged

  @AC7
  Scenario: Declined payment leaves the subscriber on Standard
    Given the subscriber's email starts with "fail"
    When the subscriber confirms the upgrade
    Then the response status code is 402
    And the response detail is "card_declined"
    And the subscriber's plan is still "Standard"

  @AC8
  Scenario: Already-Premium subscriber cannot upgrade again
    Given a Premium subscriber "premium@example.com"
    When the subscriber requests the upgrade preview
    Then the response status code is 409
    And the response detail is "already_premium"

  @AC8b
  Scenario: Already-Premium subscriber cannot be charged again via the upgrade endpoint
    Given a Premium subscriber "premium@example.com"
    When the subscriber confirms the upgrade
    Then the response status code is 409
    And the response detail is "already_premium"

  @AC9
  Scenario: Unauthenticated caller is rejected
    When an unknown email requests the upgrade preview
    Then the response status code is 401
