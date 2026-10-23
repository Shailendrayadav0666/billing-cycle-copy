# Personas: Premium Upgrade Demo (Frontend Only)

**Generated**: 2026-10-23T12:39:07Z
**Grounding**: Atlas deep dive (`spec/plans/atlas-deep-dive.md`). StreamPlex users log in and view the Billing page, and every seeded user is on the Standard plan ($20/month).

---

## Sam, Standard plan subscriber (primary)
- **Who**: an existing StreamPlex subscriber on the Standard plan, who views the Billing page after logging in.
- **Goal**: see what Premium offers and switch to it with one click.
- **Needs**: a clearly visible upgrade action; immediate, unambiguous confirmation; correct plan details afterwards (price, quality, screens, downloads, perks); an unchanged renewal date.
- **Frustrations**: a read-only billing page with no path to upgrade, and labels that contradict the plan shown.
- **Accessibility**: may use the keyboard or a screen reader, so the upgrade must be keyboard-operable and the confirmation announced.

## Priya, demo presenter (secondary)
- **Who**: a product or business stakeholder who walks executives and customers through the upgrade experience before the backend exists.
- **Goal**: a fast, convincing, repeatable demo. Clicking upgrades instantly, and a refresh resets the page for the next run.
- **Needs**: no loading delays or errors on click; the whole page visibly switches to Premium; an easy reset through a page refresh.

## Dev, frontend developer (supporting)
- **Who**: the engineer implementing and maintaining the Billing page.
- **Goal**: change the page safely, with a regression safety net where none exists today (the Atlas deep dive reports 0% test coverage).
- **Needs**: a working `npm test` with dev-only, pinned dependencies, and unit tests that prove the new behaviour and the unchanged existing display.

---

## Persona to Story Mapping

| Persona | Story | ACs most relevant |
|---|---|---|
| Sam, Standard plan subscriber | 1.1 | AC-1 to AC-8 |
| Priya, demo presenter | 1.1 | AC-4, AC-6, AC-7 |
| Dev, frontend developer | 1.1 | AC-9, AC-10 |
