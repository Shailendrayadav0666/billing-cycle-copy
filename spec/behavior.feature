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
    And 15 days remain in the 30-day billing cycle
    And a user "fail@example.com" exists with an active "Standard" subscription at $20/month

  @REQ-F-01 @REQ-F-04 @REQ-F-10 @REQ-F-11 @REQ-F-12 @REQ-F-14 @REQ-F-17
  Scenario: A standard subscriber upgrades end to end and sees Premium reflected everywhere
    Given "priya@example.com" is on the Billing page
    When she clicks "Upgrade to Premium"
    Then she sees a prorated charge of $10.00 in the confirmation modal
    When she clicks "Confirm Upgrade"
    Then her plan becomes "Premium" with quotas 10000/10/5000
    And the Billing page shows the "Premium" badge and price "$40/month"
    And her "renew_at" date is unchanged
    And no "Upgrade to Premium" button is shown any more

  @REQ-F-13 @REQ-F-16
  Scenario: A declined payment leaves the subscriber on Standard end to end
    Given "fail@example.com" is on the Billing page
    When she clicks "Upgrade to Premium" and then "Confirm Upgrade"
    Then she sees "Payment failed: Your card was declined. Your plan has not changed." in the modal
    And her plan remains "Standard"
    And the Billing page still shows the "Standard" badge and the "Upgrade to Premium" button
