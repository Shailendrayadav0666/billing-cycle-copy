# Behaviour contract for Story 1.1 — Mid-Cycle Subscription Upgrade (Standard -> Premium)
#
# Authored BEFORE the implementation, because it is the contract the code must satisfy.
# This is the story's ONLY spec file. Acceptance criteria, requirements, architecture and
# thresholds are read from their existing sources, never restated here.
#
# Tags are acceptance-criteria ids from stories.md. Tiers: B1 runs this file, B2 runs it plus
# every other unit's file, B3 adds .spec/behavior.feature (deliberately scenario-free this cycle).
#
# NOTE ON AMOUNTS (finding F-1 / F-2, requirement NFR-C4): renew_at is computed at runtime as
# today + 30 days, so days_remaining is 29 and the charge is 19.33 - not the 10.00 the Epic used
# as an illustration. No scenario below asserts a literal dollar amount. They assert the formula
# and its invariants, which is what stays true when the clock moves.

Feature: Mid-cycle subscription upgrade from Standard to Premium

  Background:
    Given the billing service is running
    And a Standard subscriber "tpg@example.com" exists with a renewal date 30 days out

  # ---------------------------------------------------------------- Group A + B: the Billing page

  @AC-1 @AC-2
  Scenario: The billing payload carries the real plan rather than a hardcoded label
    When the subscriber fetches their billing data
    Then the response plan name is "Standard"
    And the response price is "$20/month"

  @AC-3 @AC-4
  Scenario Outline: Upgrade eligibility is decided by the stored plan name
    Given the subscriber's plan is "<plan>"
    When the subscriber fetches their billing data
    Then the plan name in the response is "<plan>"
    And an upgrade is <eligible> for that plan

    Examples:
      | plan     | eligible     |
      | Standard | offered      |
      | Premium  | not offered  |

  # ---------------------------------------------------------------- Group C: the prorated quote

  @AC-5 @AC-7
  Scenario: The preview returns a complete prorated quote
    When the subscriber requests an upgrade preview
    Then the request succeeds
    And the quote names the current plan "Standard" and the new plan "Premium"
    And the quote's next renewal price is 40.0
    And the quote echoes the stored renewal date unchanged
    And the quote's prorated charge equals the proration formula for its own days remaining

  @AC-6
  Scenario: Days remaining is derived from the stored renewal date and never drops below one
    When the subscriber requests an upgrade preview
    Then the quote's days remaining is at least 1
    And the quote's days remaining is at most 30

  @AC-7
  Scenario: The prorated charge stays within the plan-difference bounds
    When the subscriber requests an upgrade preview
    Then the quote's prorated charge is greater than 0
    And the quote's prorated charge is at most 20.00

  @AC-8
  Scenario: An unknown caller cannot obtain a quote
    When an unknown caller "nobody@example.com" requests an upgrade preview
    Then the request is rejected as unauthenticated

  @AC-9
  Scenario: A caller with no billing record is refused rather than served another user's record
    Given a registered user "orphan@example.com" has no billing record
    When "orphan@example.com" requests an upgrade preview
    Then the request is rejected because the billing record was not found
    And the response does not contain any data belonging to "tpg@example.com"

  # ---------------------------------------------------------------- Group D: already-Premium guard

  @AC-10
  Scenario: A Premium subscriber cannot preview an upgrade
    Given the subscriber's plan is "Premium"
    When the subscriber requests an upgrade preview
    Then the request is rejected as already premium

  @AC-11
  Scenario: A Premium subscriber cannot execute an upgrade, and nothing changes
    Given the subscriber's plan is "Premium"
    And the subscriber's billing state is recorded
    When the subscriber confirms the upgrade
    Then the request is rejected as already premium
    And the subscriber's billing state is completely unchanged

  # ---------------------------------------------------------------- Group F: the dummy gateway

  @AC-16 @AC-17
  Scenario Outline: The payment gateway is deterministic on the email prefix
    When the gateway is asked to charge "<email>"
    Then the gateway result is "<result>"

    Examples:
      | email                | result        |
      | tpg@example.com      | success       |
      | fail@example.com     | card_declined |
      | failure@example.com  | card_declined |
      | Fail@example.com     | success       |
      | notfail@example.com  | success       |

  # ---------------------------------------------------------------- Group G: the happy path

  @AC-19 @AC-20
  Scenario: A successful upgrade flips the plan and reports the charge it took
    When the subscriber confirms the upgrade
    Then the request succeeds
    And the response reports the plan "Premium"
    And the response's charge equals the proration formula for the days that remained
    And the user record shows the plan "Premium" priced "$40/month"
    And the billing record shows the plan "Premium" priced "$40/month"

  @AC-21
  Scenario: An upgrade raises the quota ceilings without resetting consumption
    Given the subscriber has consumed some of every quota
    When the subscriber confirms the upgrade
    Then the request succeeds
    And the chat credits total is 10000
    And the chatbots total is 10
    And the document pages total is 5000
    And every quota's consumed amount is unchanged
    And every quota keeps its original id and label

  @AC-22
  Scenario: An upgrade replaces the on-demand restriction notice
    When the subscriber confirms the upgrade
    Then the on-demand notice reads "On-demand credit is available on your Premium plan."

  @AC-23
  Scenario: An upgrade does not move the renewal date
    Given the subscriber's renewal date is recorded from both stores
    When the subscriber confirms the upgrade
    Then the request succeeds
    And the renewal date in the user record is unchanged
    And the renewal date in the billing record is unchanged

  @AC-27 @AC-28
  Scenario: After upgrading, a fresh fetch reports Premium and upgrade is no longer offered
    When the subscriber confirms the upgrade
    And the subscriber fetches their billing data
    Then the response plan name is "Premium"
    And the response price is "$40/month"
    And an upgrade is not offered for that plan

  # ---------------------------------------------------------------- Group H: the declined path

  @AC-24 @AC-26
  Scenario: A declined card is reported with a fixed, non-disclosing error
    Given a Standard subscriber "fail@example.com" exists with a renewal date 30 days out
    When "fail@example.com" confirms the upgrade
    Then the request is rejected as payment required
    And the error detail is "card_declined"
    And the error message is "Your card was declined."
    And the error body contains no other fields

  @AC-25
  Scenario: A declined card mutates absolutely nothing
    Given a Standard subscriber "fail@example.com" exists with a renewal date 30 days out
    And the subscriber's billing state is recorded
    When "fail@example.com" confirms the upgrade
    Then the request is rejected as payment required
    And the subscriber's billing state is completely unchanged

  @AC-31
  Scenario: A subscriber whose payment failed is still on Standard with Standard quotas
    Given a Standard subscriber "fail@example.com" exists with a renewal date 30 days out
    When "fail@example.com" confirms the upgrade
    And "fail@example.com" fetches their billing data
    Then the response plan name is "Standard"
    And the chat credits total is 2000
    And the chatbots total is 3
    And the document pages total is 1000

  # ---------------------------------------------------------------- Group F: no client-set price

  @AC-18
  Scenario: A caller cannot choose their own price
    When the subscriber confirms the upgrade while supplying their own amount of 0.01
    Then the request succeeds
    And the response's charge equals the proration formula for the days that remained
    And the response's charge is not 0.01

  # ---------------------------------------------------------------- idempotency by guard

  @AC-11 @AC-19
  Scenario: An upgrade cannot be applied twice, so a double charge is impossible
    When the subscriber confirms the upgrade
    Then the request succeeds
    When the subscriber confirms the upgrade
    Then the request is rejected as already premium
