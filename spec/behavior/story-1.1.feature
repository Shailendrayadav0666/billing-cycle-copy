# Story 1.1 — Frontend unit-test tooling
# Covers: REQ-NF-05, REQ-NF-06 | Epic: HELIX-7344 | AIRE Framework v1.0

Feature: Frontend unit-test tooling

  Background:
    Given the frontend project in "src/frontend" with its package.json

  @AC-1
  Scenario: Test libraries are added as development dependencies only
    When the project's dependency manifest is inspected
    Then "vitest", "@testing-library/react" and "jsdom" are listed under devDependencies
    And none of them is listed under dependencies
    And the dependencies section still lists only "react", "react-dom" and "react-router-dom"

  @AC-2
  Scenario: The unit test command runs a passing Billing page smoke test
    Given the "/api/billing" response is mocked with plan_name "Standard" and price "$20/month"
    When a developer runs "npm run test" in "src/frontend"
    Then the tests run in a jsdom environment
    And a smoke test renders the Billing page and finds the "Plan & Billing" heading
    And the command exits with status 0
    And no request reaches a real "/api/billing" endpoint

  @AC-3
  Scenario: The coverage command produces a report the coverage gate can read
    When a developer runs "npm run test:coverage" in "src/frontend"
    Then a text coverage summary is printed
    And an lcov report is written to "src/frontend/coverage/lcov.info"

  @AC-4
  Scenario: Exact versions are pinned in a committed lock file and audited
    When the story's changes are committed
    Then "src/frontend/package-lock.json" is part of the commit and records the exact resolved versions of the new dev dependencies
    And "src/frontend/package-lock.json" is no longer ignored by "src/frontend/.gitignore"
    And the "npm audit" result is saved in the story's evidence

  @AC-4
  Scenario: A high or critical advisory in a new dev dependency is not accepted
    Given "npm audit" reports a high or critical advisory for a newly added dev dependency
    When the story's evidence is reviewed
    Then the story is not complete until the advisory is resolved by a non-vulnerable version
