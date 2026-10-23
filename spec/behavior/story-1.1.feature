# Behaviour contract: Story 1.1 Upgrade to Premium on the Billing page (frontend only)
# Covers: REQ-F-01..REQ-F-10, REQ-NF-01..REQ-NF-06 (spec/plans/requirements.md v1)
# Approved at the STOP CHECKPOINT. Implementations are measured against this file; never rewrite it to match code.

Feature: Upgrade to Premium on the Billing page

  Background:
    Given the user is logged in
    And the billing service returns this plan for the user:
      | plan_name | price      | renew_at     |
      | Standard  | $20/month  | Oct 30, 2026 |
    And the Standard usage cards are "Full HD (1080p)", "Can watch on 2 devices at once" and "Can download on 2 devices"
    And the Standard plan perks are "Ad-free streaming" and "Spatial audio (select titles)"

  @AC-1
  Scenario: Standard subscriber sees the upgrade button below the plan row
    When the Billing page finishes loading
    Then an "Upgrade to Premium" button is shown
    And the button appears after the "Renew at" card and before the "What's included with Standard" heading
    And the button is only as wide as its label and is left-aligned

  @AC-2
  Scenario: Premium subscriber does not see the upgrade button
    Given the billing service returns plan_name "Premium" for the user
    When the Billing page finishes loading
    Then no "Upgrade to Premium" button is shown

  @AC-2
  Scenario: Subscriber on any other plan does not see the upgrade button
    Given the billing service returns plan_name "Basic" for the user
    When the Billing page finishes loading
    Then no "Upgrade to Premium" button is shown

  @AC-2
  Scenario: Upgrade button is not shown while billing is still loading
    Given the billing service has not responded yet
    When the Billing page is opened
    Then "Loading billing..." is shown
    And no "Upgrade to Premium" button is shown

  @AC-3
  Scenario: Plan labels show the Standard plan from the billing data
    When the Billing page finishes loading
    Then the current plan badge reads "Standard"
    And the section heading reads "What's included with Standard"

  @AC-3
  Scenario: Plan labels show whatever plan the billing data names
    Given the billing service returns plan_name "Premium" for the user
    When the Billing page finishes loading
    Then the current plan badge reads "Premium"
    And the section heading reads "What's included with Premium"
    And the badge keeps the existing teal plan-badge styling

  @AC-4
  Scenario: Clicking upgrade switches the plan details to Premium without a reload
    When the Billing page finishes loading
    And the user clicks "Upgrade to Premium"
    Then the page is not reloaded
    And the plan price reads "$40/month"
    And the usage cards read:
      | label                  | value                          |
      | Video quality          | 4K Ultra HD                    |
      | Watch at the same time | Can watch on 4 devices at once |
      | Download on devices    | Can download on 6 devices      |
    And the plan perks are "Ad-free streaming", "Spatial audio (select titles)" and "Dolby Vision (select titles)"

  @AC-5
  Scenario: Renewal date is unchanged by the upgrade
    When the Billing page finishes loading
    And the user clicks "Upgrade to Premium"
    Then the "Renew at" date still reads "Oct 30, 2026"

  @AC-6
  Scenario: After upgrading, the page confirms Premium and removes the button
    When the Billing page finishes loading
    And the user clicks "Upgrade to Premium"
    Then the message "You're now on Premium!" is shown
    And no "Upgrade to Premium" button is shown
    And the current plan badge reads "Premium"
    And the section heading reads "What's included with Premium"

  @AC-6
  Scenario: Success message is not shown before any upgrade
    When the Billing page finishes loading
    Then the message "You're now on Premium!" is not shown

  @AC-7
  Scenario: Upgrading makes no request to the billing service
    When the Billing page finishes loading
    Then exactly 1 request to "/api/billing" has been made
    When the user clicks "Upgrade to Premium"
    Then still exactly 1 request has been made in total

  @AC-7
  Scenario: The upgrade is not persisted across a reload
    When the Billing page finishes loading
    And the user clicks "Upgrade to Premium"
    And the Billing page is reloaded
    Then the plan price reads "$20/month"
    And the current plan badge reads "Standard"
    And an "Upgrade to Premium" button is shown
    And the message "You're now on Premium!" is not shown

  @AC-8
  Scenario: Keyboard user upgrades with the keyboard
    When the Billing page finishes loading
    And the user moves focus to the "Upgrade to Premium" button with the Tab key
    Then the button shows a visible focus outline
    When the user presses Enter
    Then the plan price reads "$40/month"
    And the message "You're now on Premium!" is shown

  @AC-8
  Scenario: Screen readers are told about the upgrade
    When the Billing page finishes loading
    And the user clicks "Upgrade to Premium"
    Then the message "You're now on Premium!" is in a status region announced politely to assistive technology

  @AC-9
  Scenario: Standard billing display is unchanged when no upgrade happens
    When the Billing page finishes loading
    Then the heading reads "Plan & Billing"
    And the plan price reads "$20/month"
    And the "Renew at" date reads "Oct 30, 2026"
    And the usage cards read:
      | label                  | value                          |
      | Video quality          | Full HD (1080p)                |
      | Watch at the same time | Can watch on 2 devices at once |
      | Download on devices    | Can download on 2 devices      |
    And the plan perks are "Ad-free streaming" and "Spatial audio (select titles)"

  @AC-10
  Scenario: The frontend unit-test suite runs the Billing page tests
    Given the frontend dependencies are installed from the committed lock file
    When the developer runs "npm test" in "src/frontend"
    Then the Billing page unit tests under "tests/unit/" run and pass
    And the line coverage of the changed Billing page code meets unitTestCoverageMin
