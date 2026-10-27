# Personas: Premium Upgrade Demo (Frontend Only)

**Epic**: HELIX-7344 — Premium Upgrade Demo (Frontend Only)
**AIRE Framework**: v1.0

---

## P1. Standard-plan subscriber

| Attribute | Detail |
|---|---|
| Who | A logged-in StreamPlex customer on the Standard plan ($20/month: Full HD, 2 screens, 2 download devices) |
| Where they meet this epic | The Plan & Billing page (`/billing`) |
| Goal | Understand what their plan includes, and move to a better plan with as little effort as possible |
| What they need from this epic | A visible way to upgrade, an instant and clear view of what Premium gives them, and confirmation that the upgrade happened |
| Frustrations | A read-only billing page with no way to act on it; pages that hang or break without explanation |
| Accessibility needs | Must work by keyboard alone and with a screen reader, including hearing the upgrade confirmation |

## P2. Product stakeholder

| Attribute | Detail |
|---|---|
| Who | A product owner or business stakeholder watching or giving the demo |
| Where they meet this epic | The live demo of the Billing page, ahead of the full "Self-Serve Premium Upgrade" Epic |
| Goal | Judge whether the upgrade experience feels right before any backend investment is made |
| What they need from this epic | A demo that behaves the same every time, shows convincing Premium values, and resets cleanly on reload so it can be shown again |
| Frustrations | A demo that breaks in front of an audience; behaviour that can't be trusted to repeat |

---

## Persona to Story Map

| Story | P1 Standard-plan subscriber | P2 Product stakeholder |
|---|---|---|
| 1.1 Frontend unit-test tooling | | Primary |
| 1.2 Plan text follows the current plan | Primary | |
| 1.3 Fail-safe billing fetch | Primary | Secondary |
| 1.4 Upgrade button on the Standard plan | Primary | |
| 1.5 Switch the plan display to Premium on click | Primary | Secondary |
| 1.6 Post-upgrade confirmation | Primary | Secondary |
