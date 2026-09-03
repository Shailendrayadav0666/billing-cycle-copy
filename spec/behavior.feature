Feature: Mid-Cycle Subscription Upgrade — end to end
  # Cycle-level cross-story journeys (common/behavior-spec.md Section 3).
  # This cycle has exactly ONE story (Story 1), so there are no genuine cross-story
  # seams to test that Story 1's own spec/behavior/story-1.feature does not already
  # cover end to end. Per Section 6.1, this single-unit cycle still RUNS B3 on
  # Story 1 — it is not skipped, it simply has no scenarios distinct from Story 1's
  # own, because Story 1 IS the whole epic (see spec/plans/stories.md's granularity
  # note on the user's explicit single-story override).
  #
  # The scenarios below restate the two end-to-end outcomes at the @REQ level so B3
  # has something concrete to execute against requirements.md, without duplicating
  # Story 1's AC-level scenario detail.

  Background:
    Given a user "priya@example.com" exists with an active "Standard" subscription at $20/month
    And a user "fail@example.com" exists with an active "Standard" subscription at $20/month

  @REQ-F-01 @REQ-F-04 @REQ-F-10 @REQ-F-11 @REQ-F-12 @REQ-F-14 @REQ-F-17
  Scenario: A standard subscriber upgrades end to end and sees Premium reflected everywhere
    When "priya@example.com" requests the upgrade preview
    Then the response is 200
    And the response contains current_plan "Standard" and new_plan "Premium"
    When "priya@example.com" confirms the upgrade
    Then the response is 200 with status "success" and plan "Premium"
    And "priya@example.com" plan_name becomes "Premium"
    And "priya@example.com" usages become chat-credits 10000, chatbots 10, documents-pages 5000
    And "priya@example.com" renew_at is unchanged
    When "priya@example.com" views the Billing page
    Then the plan badge shows "Premium"
    And no "Upgrade to Premium" button is shown

  @REQ-F-13 @REQ-F-16
  Scenario: A declined payment leaves the subscriber on Standard end to end
    When "fail@example.com" confirms the upgrade
    Then the response is 402 with detail "card_declined"
    And "fail@example.com" plan_name remains "Standard"
    And "fail@example.com" usages are unchanged
    When "fail@example.com" views the Billing page
    Then the plan badge shows "Standard"
    And an "Upgrade to Premium" button is shown
